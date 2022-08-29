from singletonDecorator import singleton
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

"""
This class represents a DataBase that holds all the information about coins that founds by the program.
"""


@singleton
class Database:
    def __init__(self):
        self.cred = credentials.Certificate("ServiceAccountKey.json")
        firebase_admin.initialize_app(self.cred, {
            'storageBucket': 'houseeye-ea111.appspot.com'
        })

        self.db = firestore.client()
        self.bucket = storage.bucket()

    def add_user(self, user_name, cellphone, image_path):
        """
        Add new user to database.
        :param user_name: The username of the user
        :param image_path: Image path for the image
        :param cellphone: The cellphone of the user.
        :return:
        """
        try:
            if not self.db.collection('Users').where('username', '==', user_name).get():
                self.db.collection('Users').add({'username': user_name, 
                                                 'cellphone': cellphone,
                                                 'image': image_path,
                                                 'status': 'Out'})
            else:
                return "User is already inside"
        except Exception as e:
            return e.args
        return "Successfully Added"

    def delete_user(self, user_name, image_path):
        """
        Delete user from database.
        :param user_name: The user name you want to delete
        :return str:
        """
        try:
            query_ref = self.db.collection('Users').where('username', '==', user_name).get()
            for doc in query_ref:
                doc_id = doc.id
                self.db.collection("Users").document(doc_id).delete()
            blob = self.bucket.blob(image_path)
            blob.delete()
        except Exception as e:
            return e.args
        return "Successfully Deleted"

    def get_cellphones(self):
        """
        Get all cellphone numbers in the database.
        :return: List of cellphones.
        """
        return [user['cellphone'] for user in self.get_all_users()] 

    def get_user(self, user_name):
        """
        Get username.
        :param user_name: The username you need.
        :return: username
        """
        try:
            query_ref = self.db.collection('Users').where('username', '==', user_name).get()
            doc = query_ref[0].to_dict()

        except Exception as e:
            return e.args
        return doc

    def add_image(self, image_file):
        """
        Add image
        :param user_name: The user who own the image
        :param image_file: Image to upload
        :return:
        """
        try:
            blob = self.bucket.blob(image_file)
            blob.upload_from_filename(image_file)
        except Exception as e:
            return e.args
        return "Successfully Added"

    def delete_image(self, image_file):
        """
        Delete image.
        :param image_file: Image to delete
        :return:
        """
        try:
            blob = self.bucket.blob(image_file)
            blob.delete()
        except Exception as e:
            return e.args
        return "Successfully Added"

    def find_user_by_image(self, image_path):
        """
        Get username by image.
        :param image_path: Image of user
        :return: username
        """
        try:
            query_ref = self.db.collection('Users').where('image', '==', image_path).get()
            username = query_ref[0].to_dict()['username']
        except Exception as e:
            return e.args
        return username

    def find_cell_by_user(self, username):
        try:
            query_ref = self.db.collection('Users').where('username', '==', username).get()
            cell = query_ref[0].to_dict()['cellphone']
            return cell
        except Exception as e:
            return e.args
        


    def get_images(self):
        try:
            files = self.bucket.list_blobs()
        except Exception as e:
            return e.args
        return files

    def update_user(self, **kwargs):
        try:
            query_ref = self.db.collection('Users').where('username', '==', kwargs['username']).get()
            for doc in query_ref:
                doc_id = doc.id
                self.db.collection("Users").document(doc_id).set(kwargs)
        except Exception as e:
            return e.args
        return "Updated successfully"

    def get_all_users(self):
        query = self.db.collection('Users').get()
        users_details = [user.to_dict() for user in query]
        return users_details

    def create_chat(self, sender, receiver):
        chat_ref = self.db.collection('Chats').add({'contacts': {'user_1': sender, 'user_2': receiver}})
        self.db.collection('Users').where('username', '==', sender).collection('chats').document(chat_ref.id) \
            .add({'last_message': '',
                  'created_time': '00:00'})
        self.db.collection('Users').where('username', '==', receiver).collection('chats').document(chat_ref.id) \
            .add({'last_message': '',
                  'created_time': '00:00'})

    def send_message(self, sender, receiver, message):
        chat_ref = self.db.collection('Chats').where('contacts', '==', {'user_1': sender, 'user_2': receiver})

        chat_ref.collection('conversation').add({'message': message,
                                                 'sender': sender,
                                                 'receiver': receiver,
                                                 'date': '00:00'})
        self.db.collection('Users').where('username', '==', sender).collection('chats').document(chat_ref.id) \
            .set({'last_message': message})
        self.db.collection('Users').where('username', '==', receiver).collection('chats').document(chat_ref.id) \
            .set({'last_message': message})

    def load_chat(self, user1, user2):
        chat_ref = self.db.collection('Chats').where('contacts', '==', {'user_1': user1, 'user_2': user2})
        chat_messages = [user.to_dict() for user in chat_ref]
        return chat_messages

