import keyboard
import random
import json
import os

KEYBOARD_ABNT2 = "KEYBOARD_ABNT2"
KEYBOARD_QWERTY = "KEYBOARD_QWERTY"

WARNING_SHORT_PASSWORD = "WARNING_SHORT_PASSWORD"
WARNING_REPEATED_CHARACTERES = "WARNING_REPEATED_CHARACTERES"
WARNING_ATHENTICATION_FAILED = "WARNING_ATHENTICATION_FAILED"
WARNING_WRONG_PASSWORD = "WARNING_WRONG_PASSWORD"
WARNING_WRONG_PLUS_FACTOR = "WARNING_WRONG_PLUS_FACTOR"
WARNING_MISSING_USER = "WARNING_MISSING_USER"
WARNING_USER_ALREADY_EXISTS = "WARNING_USER_ALREADY_EXISTS"
WARNING_USER_ALREADY_AUTHENTICATED = "WARNING_USER_ALREADY_AUTHENTICATED"
WARNING_USER_NOT_FOUND = "WARNING_USER_NOT_FOUND"

SUCCESS = "SUCCESS"

ERROR_FAILED_TO_SAVE_DATA = "ERROR_FAILED_TO_SAVE_DATA"
ERROR_FAILED_TO_READ_DATA = "ERROR_FAILED_TO_READ_DATA"

class Encryptor:
    def __init__(self) -> None:
        self.users_data = []

        self.__current_session = None

        self.chave_teste = []

        if os.path.exists("users_data.json"):
            if self.__read_users_data() == ERROR_FAILED_TO_READ_DATA:
                self.__save_users_data()
    
    def generate_keys(self, user:str, password:str=None, password_recovery=False, keyboard_type=KEYBOARD_ABNT2) -> str:
        
        user_data = {
            "primary_key": [],
            "secondary_key": [],
            "main_key": [],
            "user": None,
            "password": [],
            "recovery_password": [],
            "keyboard_type": None,
        }

        keyboard_type = keyboard_type.upper()

        # ADDING SETTINGS
        user_data["user"] = user
        user_data["keyboard_type"] = keyboard_type

        # CREATING RANDOM KEYS
        while True:

            user_data["primary_key"], user_data["secondary_key"], user_data["main_key"] = self.__get_random_keys(amount=3, source=keyboard.characters[keyboard_type])

            if user_data["primary_key"] != user_data["secondary_key"] and user_data["primary_key"] != user_data["main_key"] and user_data["main_key"] != user_data["secondary_key"]:
                break

        # CHECKING IF IS A VALID USER AND IS NOT NONE  
        if user != None:
            for user_index in range(len(self.users_data)):
                if user == self.users_data[user_index]["user"]:
                    return WARNING_USER_ALREADY_EXISTS
        else:
            return WARNING_MISSING_USER
        
        shuffled_password = []

        # CHECKING IF PASSWORD IS TO SHORT
        if not password == None:
            if len(password) < 4:
                return WARNING_SHORT_PASSWORD

            # CREATING SHUFFLED PASSWORD
            user_data["password"] = self.__replace_repeated_chars(target=[ord(char) for char in password], source=keyboard.characters[keyboard_type])
            while True:
                shuffled_password, = self.__get_random_keys(amount=1, source=user_data["password"])
                if user_data["password"] != shuffled_password:
                    break

            print("Esse:", shuffled_password, user_data["password"])
        
        factors = self.__get_factors(user_data["password"])

        self.chave_teste = user_data["main_key"][:]

        print(user_data["main_key"], factors, user_data["password"])

        # ENCRYPTING MAIN KEY
        user_data["main_key"] = self.__encrypt_key(user_data["main_key"], user_data["primary_key"], user_data["secondary_key"], factors)
        user_data["main_key"] = self.__encrypt_key(user_data["main_key"], user_data["password"], shuffled_password, factors)

        print(user_data["main_key"])

        if not password == None:
            # IN CASE THE USER ENABELS RECOVERY_PASSWORD
            if password_recovery:
                user_data["recovery_password"] = self.__encrypt_key([ord(char) for char in password], user_data["primary_key"], user_data["secondary_key"], self.__get_factors([]))

            # STORES THE SHUFFLED PASSWORD CHARS INDEXES INTO PASSWORD KEY VALUE
            for i in range(len(user_data["password"])):
                user_data["password"][i] = shuffled_password.index(user_data["password"][i])
        
        # ADDING USER TO MEMORY AND SAVING INTO HARD DISK
        self.users_data.append(user_data)
        self.__save_users_data()
    
        return SUCCESS
    
    def __search_user(self, user:str) -> list:

        user_exists = False
        for user_data in self.users_data:
            if user_data["user"] == user:
                user_exists = True
                break
        
        if not user_exists:
            return WARNING_USER_NOT_FOUND
        
        return user_data

    def __replace_repeated_chars(self, target:list, source:list) -> list:
        target = target[:]
        length = len(target)
        for i in range(length):
            for j in range(length):
                if i == j: 
                    break
                else:
                    if target[i] == target[j]:
                        target[i] = self.__get_non_repeated_char(target=target, source=source)
        return target

    def __get_non_repeated_char(self, target:list, source:list) -> int:
        for char in source:
            if char not in target:
                return char
    
    def __get_factors(self, password:list) -> dict:
        if len(password) != 0:
            plus_factor = self.__get_plus_factor(password)
            return {
                "plus": plus_factor,
                "times": self.__get_times_factor(plus_factor)
            }
        return {
            "plus": 365,
            "times": 12
        }

    def __get_plus_factor(self, x:list) -> int:
        plus_factor = 0

        for i in range(len(x)):
            plus_factor += (x[i] * (i + 1))

        return plus_factor

    def __get_times_factor(self, plus_factor:list):
        return (plus_factor % 30) + 1 # CHANGE THE 30 VALUE TO INCREASE THE SPECTRUM OF ITERATIONS WHEN ENCRYPTING/DECRYPTING

    def __get_random_keys(self, amount:int, source:list) -> list:
        random_keys = [None for _ in range(amount)]
        for i in range(amount):
            random_keys[i] = self.__shuffle(source)
        
        return random_keys

    def __shuffle(self, x:list) -> list:
        length = len(x)
        x_copy = x[:]
        for i in range(length):
            aux = x_copy[i]
            index = random.randint(0, length - 1)
            x_copy[i] = x_copy[index]
            x_copy[index] = aux
        
        return x_copy
    
    def __read_users_data(self) -> str:
        try:
            with open("users_data.json", "r") as json_file:
                self.users_data = json.load(json_file)
            return SUCCESS
        except:
            return ERROR_FAILED_TO_READ_DATA
    
    def __save_users_data(self) -> None:
        try:
            with open("users_data.json", "w") as json_file:
                json.dump(self.users_data, json_file, indent=4)
        except:
            return ERROR_FAILED_TO_SAVE_DATA

    def __get_char_index(self, array:list, char:str) -> int:
        for i in range(len(array)):
            if array[i] == char:
                return i
        return -1

    def __encrypt_key(self, key:list, key_1:list, key_2:list, factors:dict) -> list:

        length = len(key_1)

        if length == len(key_2) and length > 0:
            print(None, "AQUI")
            key = key[:]
            key_1 = key_1[:]
            key_2 = key_2[:]

            for _ in range(factors["times"]):
                for i in range(len(key)):
                    key_1_char_index = self.__get_char_index(key_1, key[i])
                    if key_1_char_index != -1:
                        key[i] = key_2[(key_1_char_index + factors["plus"] + i) % length]
        
        return key

    def __decrypt_key(self, encrypted_key:list, key_1:list, key_2:list, factors:dict) -> list:

        length = len(key_1)

        if length == len(key_2) and length > 0:
            encrypted_key = encrypted_key[:]
            key_1 = key_1[:]
            key_2 = key_2[:]

            for _ in range(factors["times"]):
                for i in range(len(encrypted_key)):
                    key_2_char_index = self.__get_char_index(key_2, encrypted_key[i])
                    if key_2_char_index != -1:
                        encrypted_key[i] = key_1[(key_2_char_index - factors["plus"] - i) % length]

        return encrypted_key
    
    def start_session(self, user:str, password:str) -> str|None:
        
        self.__current_session = self.__search_user(user=user)
        if self.__current_session == WARNING_USER_NOT_FOUND:
            self.__current_session = None
            return WARNING_USER_NOT_FOUND            
        
        shuffled_password = []

        if password != None:
            password_aux = self.__replace_repeated_chars(target=[ord(char) for char in password], source=keyboard.characters[self.__current_session["keyboard_type"]])
            print(password_aux, "QQQQQQQQ")
            if len(self.__current_session["password"]) == len(password):
                shuffled_password = [None for _ in self.__current_session["password"]]
                for i in range(len(shuffled_password)):
                    shuffled_password[self.__current_session["password"][i]] = password_aux[i]
                self.__current_session["password"] = password_aux

        factors = self.__get_factors(self.__current_session["password"])
        print(shuffled_password, self.__current_session["password"])

        self.__current_session["main_key"] = self.__decrypt_key(self.__current_session["main_key"], self.__current_session["password"], shuffled_password, factors)
        self.__current_session["main_key"] = self.__decrypt_key(self.__current_session["main_key"], self.__current_session["primary_key"], self.__current_session["secondary_key"], factors)

        if not self.__successful_login():
            self.__current_session = None
            return WARNING_ATHENTICATION_FAILED
        
        print(self.__current_session["main_key"], factors)
        print(self.chave_teste == self.__current_session["main_key"])
        return SUCCESS
    
    def __successful_login(self) -> bool:

        keyboard_chars = [chr(char) for char in keyboard.characters[self.__current_session["keyboard_type"]]]
        message = "".join(keyboard_chars)
        encrypted_message = self.encrypt(message)
        decrypted_message = self.decrypt(encrypted_message)

        if message == decrypted_message:
            return True
        else:
            return False
    
    def end_session(self) -> str:
        self.__current_session = None
    
    def encrypt(self, message:str=None) -> str|None:
        if self.__current_session != None:

            encrypted_message = [ord(message[i]) for i in range(len(message))]
            
            factors = self.__get_factors(self.__current_session["password"])

            print(factors)

            for _ in range(factors["times"]):
                for i in range(len(encrypted_message)):
                    key_1_char_index = self.__get_char_index(self.__current_session["main_key"], encrypted_message[i])
                    if key_1_char_index != -1:
                        encrypted_message[i] = self.__current_session["primary_key"][(key_1_char_index + factors["plus"] + i) % keyboard.lengths[self.__current_session["keyboard_type"]]]

            encrypted_message = [chr(encrypted_message[i]) for i in range(len(encrypted_message))]
            return "".join(encrypted_message)
            
        
    def decrypt(self, encrypted_message:str=None) -> str|None:
        if self.__current_session != None:

            message = [ord(encrypted_message[i]) for i in range(len(encrypted_message))]

            factors = self.__get_factors(self.__current_session["password"])

            for _ in range(factors["times"]):
                for i in range(len(message)):
                    key_2_char_index = self.__get_char_index(self.__current_session["primary_key"], message[i])
                    if key_2_char_index != -1:
                        message[i] = self.__current_session["main_key"][(key_2_char_index - factors["plus"] - i) % keyboard.lengths[self.__current_session["keyboard_type"]]]

            message = [chr(message[i]) for i in range(len(message))]
            return "".join(message)

    def change_pasword(self, user:str, old_password:str, new_password:str):
        self.end_session()

    def change_keys(self, user:str, old_password:str, new_password:str):
        self.end_session()
    
    def recovery_password(self, user:str) -> str:

        user_data = self.__search_user(user=user)
        
        factors = self.__get_factors([])
        decrypted_recovery_password = self.__decrypt_key(user_data["recovery_password"], user_data["primary_key"], user_data["secondary_key"], factors)
        recovery_password = [chr(char) for char in decrypted_recovery_password]

        return "".join(recovery_password)
    
#print(Encryptor().generate_keys("IVAN", "236589", keyboard_type=KEYBOARD_QWERTY, plus_factor=1894))
encryptor = Encryptor()
encryptor.generate_keys(user="DODO", password="ø¾9´çQìç_ÒöStÈás§OPÒ¬ÌýáÄL0H½¤®Ãó¸K2ÌbCÁÁ_kt4vgì]ìÊö·¢u9èm$a¥4re~áå/À&Ó+Ñ/U³ö!¨|d", password_recovery=True, keyboard_type=KEYBOARD_ABNT2)
print(encryptor.start_session("DODO", "ø¾9´çQìç_ÒöStÈás§OPÒ¬ÌýáÄL0H½¤®Ãó¸K2ÌbCÁÁ_kt4vgì]ìÊö·¢u9èm$a¥4re~áå/À&Ó+Ñ/U³ö!¨|d"))
message = encryptor.encrypt("Este mundo está tão sofrido que é melhor rep&ensar o que se f4la 7894561230 Vezes")
print(message)
print(encryptor.decrypt(message))
print(encryptor.recovery_password("IRANILDO"))

