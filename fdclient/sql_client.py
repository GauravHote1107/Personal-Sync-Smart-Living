import pymysql
import pymysql.cursors

import numpy as np


class SQLClient:
    def __init__(self):
        self.connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="Gh1947",
            database="smart_home",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.settings_cache = self.update_settings_cache()

    def update_settings_cache(self, user_name: str = None):
        settings_cache = {}
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM ku_settings")
            settings = cursor.fetchall()

            for setting in settings:
                if user_name and setting["user_name"] != user_name:
                    continue

                pin_number = f"D{setting['pin_number']}"
                if setting["user_name"] in settings_cache:
                    settings_cache[setting["user_name"]][pin_number] = setting["value"]
                else:
                    settings_cache[setting["user_name"]] = {pin_number: setting["value"]}

                if user_name and setting["user_name"] == user_name:
                    break

        return settings_cache

    def get_user_settings(self, user: str):
        return self.settings_cache.get(user, None)

    def get_face_encodings(self):
        face_encodings = []
        face_names = {}

        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM user_parameters")
            encodings = cursor.fetchall()

            for encoding in encodings:
                face_encodings.append(np.frombuffer(encoding["encoding"], dtype=np.float64))
                face_names[encoding["name"]] = encoding["priority"]

        return face_encodings, face_names
