import json

from flask import Flask, request, jsonify

from breakages_database import BreakagesDatabase
from users_database import UsersDatabase, UserNotFoundError

app = Flask(__name__)
breakages_db = BreakagesDatabase()
users_db = UsersDatabase()


def check_password(request_data):
    return users_db.check_password(request_data['user_id'],
                                   request_data['password'])


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    if not check_password(json.loads(request.data)):
        return {'status': 'error', 'message': 'wrong user or password'}
    try:
        return {'status': 'ok', 'role': users_db.get_user_role(user_id)}
    except UserNotFoundError:
        return {'status': 'error', 'message': 'wrong user or password'}


@app.route('/breakages', methods=['GET'])
def get_free_breakages():
    result = [{'id': id_, 'place': place, 'time': time, 'description': description}
              for id_, place, time, description in breakages_db.get_free_breakages()]
    return jsonify(result)


@app.route('/user/<int:engineer_id>/breakages', methods=['GET'])
def get_breakages_for_engineer(engineer_id):
    result = [{'id': id_, 'place': place, 'time': time, 'description': description}
              for id_, place, time, description in breakages_db.get_engineer_breakages(engineer_id)]
    return jsonify(result)


@app.route('/breakages', methods=['POST'])
def add_new_breakage():
    if not request.is_json:
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    breakages_db.add_new_breakage(data['place'], data['time'], data['description'])
    return {"status": "ok"}


@app.route('/breakages/<int:breakage_id>/take', methods=['POST'])
def take_breakage(breakage_id):
    if not request.is_json:
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    if users_db.get_user_role(data['user_id']) != 'ENGINEER':
        return {"status": "error", "message": "this operation is for engineers only"}
    result = breakages_db.take_breakage(breakage_id, data['user_id'])
    return {'status': "ok" if result else "failed"}


@app.route('/breakages/<int:breakage_id>/fix', methods=['POST'])
def report_breakage_fixed(breakage_id):
    breakages_db.report_breakage_fixed(breakage_id)
    return {"status": "ok"}


if __name__ == '__main__':
    app.run()
