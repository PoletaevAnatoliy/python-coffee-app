import json

from flask import Flask, request, jsonify

from database import BreakagesDatabase

app = Flask(__name__)
db = BreakagesDatabase()


@app.route('/breakages', methods=['GET'])
def get_free_breakages():
    result = [{'id': id_, 'place': place, 'time': time, 'description': description}
              for id_, place, time, description in db.get_free_breakages()]
    return jsonify(result)


@app.route('/breakages', methods=['POST'])
def add_new_breakage():
    if not request.is_json:
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    db.add_new_breakage(data['place'], data['time'], data['description'])
    return {"status": "ok"}


@app.route('/breakages/<int:breakage_id>/take', methods=['POST'])
def take_breakage(breakage_id):
    if not request.is_json:
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    result = db.take_breakage(breakage_id, data['engineer_id'])
    return {'status': "ok" if result else "failed"}


@app.route('/breakages/<int:breakage_id>/fix', methods=['POST'])
def report_breakage_fixed(breakage_id):
    db.report_breakage_fixed(breakage_id)
    return {"status": "ok"}


if __name__ == '__main__':
    app.run()
