import cv2
import face_recognition
import numpy as np

from sql_client import SQLClient
from node_client import NodeClient

video_capture = cv2.VideoCapture(0)

client = SQLClient()
node_client = NodeClient()

known_face_encodings, face_priorities = client.get_face_encodings()

known_face_names = list(face_priorities.keys())
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    ret, frame = video_capture.read()

    if process_this_frame:
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow("Video", frame)


    max_priority = (-9999, "Unknown")
    if "Unknown" in face_names:
        face_names.remove("Unknown")

    for face_name in face_names:
        if face_priorities[face_name] > max_priority[0]:
            max_priority = (face_priorities[face_name], face_name)

    if (settings := client.get_user_settings(max_priority[1])) != None:
        for setting in settings:
            node_client.update_pin(setting, settings[setting])
    else:
        for setting in node_client.values_cache:
            node_client.reset_pin(setting)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        for setting in node_client.values_cache:
            node_client.reset_pin(setting)
        break

video_capture.release()
cv2.destroyAllWindows()
