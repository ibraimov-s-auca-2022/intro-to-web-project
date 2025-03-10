from flask import Flask, jsonify, request
from db import db, User, Post, Like, init_db
from auth import Auth
from config import SERVER_PORT

app = Flask(__name__)
init_db(app)

@app.route('/ping')
def ping():
    return "pong"

def check_session(session_id):
    if Auth.check_session(session_id):
        return True
    return False

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing username, email, or password"}), 400
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.password_hash != data['password']:
        return jsonify({"error": "Incorrect password"}), 401

    session_id = Auth.login(email=data['email'], user_id=user.id)
    return jsonify({"session_id": session_id}), 200

@app.route('/logout', methods=['DELETE'])
def logout():
    data = request.get_json()
    if 'session_id' not in data:
        return jsonify({"error": "Missing session_id"}), 404
    if not Auth.check_session(data['session_id']):
        return jsonify({"error": "Invalid session_id"}), 401
    Auth.logout(data['session_id'])
    return jsonify({"session_id": None}), 200

@app.route('/users', methods=['GET'])
def get_users():
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401

    users = User.query.all()
    user_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for user in users
    ]
    return jsonify(user_list)
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401
    user = User.query.get(id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing username, email, or password"}), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=data['password']  # Тут нужно захешировать пароль
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "created_at": new_user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 201


@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401
    user = User.query.get(Auth.get_user_id(data['session_id']))

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User {id} and all related posts deleted successfully"}), 200

@app.route('/posts', methods=['GET'])
def get_posts():
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401

    posts = Post.query.all()

    post_list = [
        {
            "id": post.id,
            "user_id": post.user_id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for post in posts
    ]

    return jsonify(post_list)

@app.route('/post/<int:id>', methods=['GET'])
def get_post(id):
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401
    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({
        "id": post.id,
        "user_id": post.user_id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at": post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
    })

@app.route('/post', methods=['POST'])
def create_post():
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Missing title, content"}), 400

    user = User.query.get(Auth.get_user_id(data['session_id']))
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_post = Post(
        title=data['title'],
        content=data['content'],
        user_id=Auth.get_user_id(data['session_id']),
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({
        "id": new_post.id,
        "title": new_post.title,
        "content": new_post.content,
        "user_id": new_post.user_id,
        "created_at": new_post.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 201
@app.route('/post/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401

    if not data or 'title' not in data or 'content' not in data or 'session_id' not in data:
        return jsonify({"error": "Missing title or content"}), 400

    user_id = Auth.get_user_id(data['session_id'])

    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if post.user_id != user_id:
        return jsonify({"error": "User not found"}), 401

    post.title = data['title']
    post.content = data['content']

    db.session.commit()

    return jsonify({
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id,
        "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@app.route('/post', methods=['DELETE'])
def delete_post():
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401
    if 'post_id' not in data:
        return jsonify({"error": "Missing post_id"}), 400

    post = Post.query.get(data["post_id"])

    if post.user_id != Auth.get_user_id(data['session_id']):
        return jsonify({"error": "User not found"}), 401

    if not post:
        return jsonify({"error": "Post not found"}), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": f"Post {data['post_id']} deleted successfully"}), 200


@app.route('/like', methods=['PUT'])
def like_post():
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401

    if  'post_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400

    user_id = Auth.get_user_id(data['session_id'])
    post = Post.query.get(data['post_id'])

    if not post:
        return jsonify({"error": "Post not found"}), 404

    existing_like = Like.query.filter_by(post_id=data['post_id'], user_id=user_id).first()

    if existing_like:
        return jsonify({"message": "User has already liked this post"}), 200

    new_like = Like(post_id=data['post_id'], user_id=user_id)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({
        "post_id": data['post_id'],
        "user_id": user_id,
        "message": "Like added successfully"
    }), 201

@app.route('/like/<int:post_id>', methods=['DELETE'])
def unlike_post(post_id):
    data = request.get_json()
    if not check_session(data["session_id"]):
        return jsonify({"error": "Invalid session_id"}), 401

    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing user_id"}), 400

    user_id = data['user_id']
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()

    if not existing_like:
        return jsonify({"message": "User has not liked this post"}), 200

    db.session.delete(existing_like)
    db.session.commit()

    return jsonify({
        "post_id": post_id,
        "user_id": user_id,
        "message": "Unlike deleted successfully"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=SERVER_PORT)
