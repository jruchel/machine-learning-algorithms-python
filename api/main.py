from flask import Flask, json, request
from flask_cors import CORS, cross_origin
from sklearn.linear_model import LinearRegression
from algorithms.Model import Model
from sklearn.neighbors import KNeighborsClassifier
import os

api = Flask(__name__)
cors = CORS(api)
api.config['CORS_HEADERS'] = 'Content-Type'


@api.after_request
def cleanup(response):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f.endswith(".pickle"):
            os.remove(f)
    return response


@api.route('/algorithms', methods=['GET'])
@cross_origin()
def algorithms():
    algos = ['linear-regression', 'k-nearest-neighbours']
    return json.dumps(algos)


@api.route('/algorithms/k-nearest-neighbours', methods=['GET', 'POST'])
@cross_origin()
def k_nearest_neighbours():
    try:
        arguments = request.args
        separator = arguments.get('separator')
        predicting = arguments.get('predicting')
        file = request.files['data']
        neighbours = arguments.get('neighbours')
        knn = Model(KNeighborsClassifier(n_neighbors=int(neighbours)))
        accuracy = knn.train(file, separator, predicting)
        return json.dumps({"accuracy": accuracy})
    except Exception as error:
        return str(error)


@api.route('/algorithms/linear-regression', methods=['GET', 'POST'])
@cross_origin()
def linear_regression():
    try:
        arguments = request.args
        separator = arguments.get('separator')
        predicting = arguments.get('predicting')
        save = ''
        if arguments.get('save') == 'true':
            save = True
        else:
            save = False
        savename = ''
        if save is True:
            savename = "{}-{}".format(arguments.get('savename'), arguments.get('usersecret'))

        file = request.files['data']
        regression = Model(LinearRegression())
        accuracy = regression.train(file, separator, predicting)
        intercept = regression.model.intercept_
        coefficients = regression.model.coef_
        if save:
            regression.save(savename)
            file_data = open("{}.pickle".format(savename), "rb").read()
            return json.dumps({
                "accuracy": accuracy,
                "intercept": intercept,
                "coefficients": coefficients.tolist(),
                "file": str(file_data)
            })
        else:
            return json.dumps({
                "accuracy": accuracy,
                "intercept": intercept,
                "coefficients": coefficients.tolist()})
    except Exception as error:
        return str(error)


@api.route('/read', methods=['POST'])
@cross_origin()
def read_from_database():
    return ""


@api.route('/save', methods=['POST'])
@cross_origin()
def save_to_database():
    return ""


def fit_neighbours(x_train, y_train, x_test, y_test):
    best_score = 0
    best_neighbours = 0
    for i in range(1, 100):
        model = KNeighborsClassifier(n_neighbors=i)
        model.fit(x_train, y_train)
        accuracy = model.score(x_test, y_test)
        if accuracy > best_score:
            best_score = accuracy
            best_neighbours = i
    return best_neighbours, best_score


if __name__ == "__main__":
    api.run(host='0.0.0.0')
    input("Press enter to exit")

# TODO try zipping the file and sending it that way, maybe encoding will work
