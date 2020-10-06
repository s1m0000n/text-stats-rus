from flask import Flask, render_template, jsonify, request
from wrappers_tp import HtmlTP

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/process')
def process():
    text = tuple(request.args.items())[0][0]
    tp = HtmlTP(text)
    return jsonify({'morph_analysis_table': tp.morhp_analysis(include_punct=True),
                    'gen_stat_data': tp.gen_stats(),
                    'pos_stat_table': tp.pos_freq(),
                    'pos_stat_graph': tp.pos_freq_graph()})


if __name__ == '__main__':
    app.run()
