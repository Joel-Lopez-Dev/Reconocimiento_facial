"""
------------- REGISTRO DE USUARIO --------------------------------------------
Entorno Virtual Face_Recognition
Dimensiones de video: 640x480
Dimensiones de Registro : 320x360
"""

import cv2
import numpy as np
import dlib
import pickle
import os
import face_recognition

# ----------------------------------------------------------
#     Verificación de existencia de archivo .pickle
# ----------------------------------------------------------
path = "faces_encodings.pickle"
try:
    with open(path, "rb") as f:
        data = pickle.load(f)
        box_encodings = data["encodings"]
        box_names = data["names"]
        print("[INFO] Cargando el archivo faces_encodings.pickle.....")
        print("[INFO] Número de registros en dataset:", len(box_encodings))
        print("[INFO] Usuarios registrados:", box_names)

except:
    foo = 3
    with open(path, "wb") as f:
        pickle.dump(foo, f)
        print("[INFO] Se creará archivo faces_encodings.pickle para codificación")
        box_encodings = []
        box_names = []

# ----------------------------------------------------------
#        Definición de funciones
# ----------------------------------------------------------

def pantalla_inicial():
    print("------------------------------------------------")
    print("             REGISTRO DE USUARIO                ")
    print("------------------------------------------------")

def nombre_usuario():
    pantalla_inicial()
    nombre = input('>>> Ingrese nombre de nuevo usuario: ')
    name_window = "REGISTRO DE USUARIO / " + nombre
    return nombre, name_window

# ----------------------------------------------------------
#        Detección automática de cámara disponible
# ----------------------------------------------------------
captura = None
for i in range(3):
    cap = cv2.VideoCapture(i+1)
    if cap.isOpened():
        captura = cap
        print(f"[INFO] Cámara detectada en el índice {i}")
        break
if captura is None:
    print("[ERROR] No se encontró ninguna cámara disponible.")
    exit()

w_video = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
h_video = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))

# ----------------------------------------------------------
color = (0, 0, 255)
Rectangle = np.zeros((h_video, w_video, 3), np.uint8)
Rectangle[:, :] = [0, 0, 0]

# ----------------------------------------------------------
deteccion = False
Registro_Nuevo = True
detector = dlib.get_frontal_face_detector()

nombreUsuario, name_window = nombre_usuario()
print("[INFO] Usuario a registrar:", nombreUsuario)

while True:
    grabbed, imagen = captura.read()
    if not grabbed:
        break

    ROI = imagen[40:400, 160:480]
    escala_gris = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
    rects = detector(escala_gris, 1)

    deteccion = len(rects) > 0
    color = (0, 255, 0) if deteccion else (0, 0, 255)

    suma = cv2.addWeighted(Rectangle, 0.5, imagen, 0.5, 0)
    suma[40:400, 160:480] = ROI

    # Marco
    cv2.line(suma, (160, 40), (220, 40), color, 2)
    cv2.line(suma, (160, 40), (160, 100), color, 2)
    cv2.line(suma, (160, 400), (220, 400), color, 2)
    cv2.line(suma, (160, 400), (160, 340), color, 2)
    cv2.line(suma, (480, 40), (420, 40), color, 2)
    cv2.line(suma, (480, 40), (480, 100), color, 2)
    cv2.line(suma, (480, 400), (480, 340), color, 2)
    cv2.line(suma, (480, 400), (420, 400), color, 2)

    tecla = cv2.waitKey(25) & 0xFF

    if tecla == ord('g') and Registro_Nuevo and deteccion:
        cv2.destroyWindow(name_window)
        cv2.imshow("Rostro Registrado", ROI)
        cv2.waitKey(2000)
        Registro_Nuevo = False

        confirmacion = input("[INFO] Confirme registro [y/n]: ")
        if confirmacion.lower() == "y":
            print("[INFO] Codificando imagen de rostro...")

            os.makedirs("Usuarios", exist_ok=True)
            cv2.imwrite("Usuarios/" + nombreUsuario + ".jpg", ROI)

            current_image = face_recognition.load_image_file("Usuarios/" + nombreUsuario + ".jpg")
            face_encode = face_recognition.face_encodings(current_image)[0]
            box_encodings.append(face_encode)
            box_names.append(nombreUsuario)

            print("[INFO] Rostro guardado exitosamente.")
            print("[INFO] Registro adicionado: " + nombreUsuario)
            print("[INFO] Total de registros:", len(box_encodings))

            data = {"encodings": box_encodings, "names": box_names}
            with open(path, "wb") as f:
                pickle.dump(data, f)

            cv2.destroyWindow("Rostro Registrado")
            opcion = input("[INFO] ¿Nuevo registro (n) o salir (s)?: ")

            if opcion.lower() == "n":
                Registro_Nuevo = True
                nombreUsuario, name_window = nombre_usuario()
                print("[INFO] Usuario a registrar:", nombreUsuario)
            else:
                print("Cerrando aplicación.")
                break
        else:
            cv2.destroyWindow("Rostro Registrado")
            print("[INFO] Repetir captura para usuario:", nombreUsuario)
            Registro_Nuevo = True

    elif tecla == 27:  # ESC
        break
    else:
        cv2.imshow(name_window, suma)

captura.release()
cv2.destroyAllWindows()

