import uuid


class Auth:
    sessions = {}

    def login(email, user_id):
        session_id = str(uuid.uuid4())
        Auth.sessions[session_id] = {"email": email, "user_id": user_id}
        return session_id

    def logout(session_id):
        for session in Auth.sessions:
            print(session)
        Auth.sessions.pop(session_id)
        print("Logged out")
        for session in Auth.sessions:
            print(session)

    def check_session(session_id):
        return session_id in Auth.sessions

    def get_user_id(session_id):
        return Auth.sessions[session_id]["user_id"]




