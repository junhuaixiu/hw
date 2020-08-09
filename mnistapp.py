import os
import time
from flask import Flask, request, jsonify, make_response, abort
from werkzeug.utils import secure_filename
from mnist_soft import predict
from cas1 import createKeySpace, insertData, deleteData

UPLOAD_FOLDER = 'uploaded_images'
ALLOWED_EXTENSIONS = set(['JPG', 'PNG', 'png', 'jpg', 'jpeg', 'bmp'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

numbers = []
session = createKeySpace("mnist")


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.',  1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/numbers', methods=['GET'])
def get_numbers():
    return jsonify({'numbers': numbers})


@app.route('/numbers/<int:number_id>', methods=['GET'])
def get_number(number_id):
    number = [number for number in numbers if number['id'] == number_id]
    if len(number) == 0:
        abort(404)
    return jsonify({'number': number[0]})


@app.route('/numbers/<int:number_id>', methods=['DELETE'])
def delete_number(number_id):
    number = [number for number in numbers if number['id'] == number_id]
    if len(number) == 0:
        abort(404)
    numbers.remove(number[0])
    # delete data in cassandra table
    deleteData(session, number_id)
    return jsonify({'Delete': "Success"})


@app.route('/numbers', methods=['POST'])
def create_number():
    # check if the post request has the file part
    if 'file' not in request.files:
        abort(400)
    file = request.files['file']
    # check if the file has the allowed format
    if not (file and allowed_file(file.filename)):
        abort(422)
    filename = secure_filename(file.filename)
    saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(saved_path)
    # add new number to numbers
    prediction = predict(saved_path)
    id = 1 if len(numbers) == 0 else numbers[-1]['id'] + 1
    number = {
        'id': id,
        'file_name': filename,
        'time': time.time(),
        'prediction': prediction
    }
    numbers.append(number)
    # add data in the cassandra table
    insertData(session, id, filename, prediction, time.time())
    return jsonify({"upload status": "success"}), 201


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}, 400))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(422)
def unprocessable_entity(error):
    return make_response(jsonify({'error': 'Unprocessable entity'}, 422))


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,debug=True)
