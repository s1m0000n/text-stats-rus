from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/process')
def process():
    text = tuple(request.args.items())[0][0]
    print(text)
    return jsonify({'sample': 'sample_result'})


if __name__ == '__main__':
    app.run()
