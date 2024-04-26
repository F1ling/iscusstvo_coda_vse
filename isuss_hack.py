
import os
import sqlite3
from playsound import playsound
import cv2
from deepface import DeepFace

# Пути к базам данных
DB_PATHS = {
    "angry": "angry.db",
    "sad": "sad.db",
    "happy": "happy.db",
    "fear": "fear.db",
    "surprise": "surprise.db",
    "neutral": "neutral.db",
    "disgust": "disgust.db",
}

# Пути к папкам с музыкой (измените на ваши пути)
MUSIC_DIRS = {
    "angry": "C:\\Users\\Дом\\OneDrive\\Документы\\porn\\angry_music",
    "sad": "C:\\Users\\Дом\\OneDrive\\Документы\\porn\\sad_music",
    "happy": "C:\\Users\\Дом\\OneDrive\\Документы\\porn\\happy_music",
    "surprise": "C:\\Users\\Дом\\OneDrive\\Документы\\porn\\surprise_music",
    "fear": "C:\\Users\\Дом\\OneDrive\\Документы\\porn\\fear_music",
    "neutral": "C:\\Users\\Дом\\OneDrive\\Документы\\porn\\neutral_music",
    "disgust": "C:\\Users\\Дом\\OneDrive\\Документы\\porn\\disgust_music"
}

def create_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tracks
                 (title text, path text)''')
    conn.commit()
    conn.close()

def add_track(db_name, title, path):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO tracks (title, path) VALUES (?, ?)", (title, path))
    conn.commit()
    conn.close()

def add_tracks_to_db(db_name, music_dir):
    for filename in os.listdir(music_dir):
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            add_track(db_name, filename[:-4], os.path.join(music_dir, filename))

# Создание баз данных и добавление треков
for emotion, db_path in DB_PATHS.items():
    create_db(db_path)
    add_tracks_to_db(db_path, MUSIC_DIRS[emotion])

def play_random_track_by_emotion(emotion):
    conn = sqlite3.connect(DB_PATHS[emotion])
    c = conn.cursor()
    c.execute("SELECT path FROM tracks WHERE title = ? ORDER BY RANDOM() LIMIT 1", (emotion,))
    result = c.fetchone()
    conn.close()
    if result:
        track_path = result[0]
        playsound(track_path)
    else:
        print(f"Трек для эмоции '{emotion}' не найден.")

def draw_emotion_info(frame, emotion):
    """Отображает информацию об эмоции на видео."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"Emotion: {emotion}", (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

cap = cv2.VideoCapture(0)  # Индекс камеры

previous_emotion = None

def analyze_emotion():
    global previous_emotion

    ret, frame = cap.read()
    if not ret:
        return

    analyze_face = DeepFace.analyze(frame, ["emotion"], enforce_detection=False)
    dominant_emotion = analyze_face[0]["dominant_emotion"]

    if dominant_emotion != previous_emotion:
        print("Emotion: ", dominant_emotion)
        previous_emotion = dominant_emotion

    play_random_track_by_emotion(dominant_emotion)

    draw_emotion_info(frame, dominant_emotion)  # Отображение эмоции
    cv2.imshow("Webcam Emotions", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cap.release()
        cv2.destroyAllWindows()

while True:
    analyze_emotion()
    