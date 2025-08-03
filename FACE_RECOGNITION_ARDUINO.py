import cv2
import face_recognition
import pickle
import numpy as np
import serial
import time


# ---- Abrir puerto serial para Arduino ----
try:
    arduino = serial.Serial("COM5", 9600, timeout=1)
    print("[INFO] Puerto serial COM5 abierto correctamente.")
except serial.SerialException:
    print("[ERROR] No se pudo abrir el puerto serial COM4. Verifica conexión.")
    arduino = None

# ----------------------------------------------------------
#     Carga de archivo de codificaciones previamente guardado
# ----------------------------------------------------------
path = "faces_encodings.pickle"
try:
    with open(path, "rb") as f:
        data = pickle.load(f)
        known_encodings = data["encodings"]
        known_names = data["names"]
        print("[INFO] Cargando el archivo faces_encodings.pickle.....")
        print("[INFO] Número de registros en dataset:", len(known_encodings))
        print("[INFO] Usuarios registrados:", known_names)
except Exception as e:
    print("[ERROR] No se pudo cargar el archivo de codificaciones:", e)
    exit()

# ----------------------------------------------------------
#     Detección automática de cámara disponible
# ----------------------------------------------------------
captura = None
for i in range(3):
    cap = cv2.VideoCapture(1)
    if cap.isOpened():
        captura = cap
        print(f"[INFO] Cámara detectada en el índice {i}")
        break

if captura is None:
    print("[ERROR] No se encontró ninguna cámara disponible.")
    exit()

last_sent_value = None

# ----------------------------------------------------------
#     Bucle principal de captura y reconocimiento
# ----------------------------------------------------------
while True:
    ret, frame = captura.read()

    if not ret or frame is None:
        print("[ERROR] No se pudo capturar frame de la cámara.")
        continue

    # Redimensionar el frame para mejorar rendimiento (escala 1/4)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detección y codificación
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = []
    if len(face_locations) > 0:
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    found_match = False
    for encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        name = "Desconocido"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            for i in matchedIdxs:
                name = known_names[i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)
            found_match = True
        face_names.append(name)

    # Enviar señal a Arduino solo si cambia el estado
    if arduino is not None:
        valor_actual = '4' if found_match else '0'
        if valor_actual != last_sent_value:
            arduino.write(valor_actual.encode())
            last_sent_value = valor_actual

    # Mostrar resultados
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Escalar coordenadas al tamaño original
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Dibujar rectángulo y etiqueta
        color = (0, 255, 0) if name != "Desconocido" else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.9, (0, 0, 0), 2)

    cv2.imshow("Reconocimiento Facial", frame)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == 27:  # ESC
        break

# ----------------------------------------------------------
#     Liberar recursos
# ----------------------------------------------------------
if arduino is not None:
    arduino.write('0'.encode())  # Apagar actuador
    time.sleep(0.1)
    arduino.close()

captura.release()
cv2.destroyAllWindows()

