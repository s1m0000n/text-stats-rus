from flask import Flask, render_template, jsonify, request

from wrappers_tp import HtmlTP

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/process')
def process():
    try:
        text = tuple(request.args.items())[0][0]
    except IndexError:
        return jsonify({'info_field': 'Пожалуйста, введите текст'})
    else:
        tp = HtmlTP(text)
        return jsonify({'gen_stat_data': tp.gen_stats_data(),
                        'gen_stat_data_with_punct': tp.gen_stats_with_punct(),
                        'gen_stat_data_wo_punct': tp.gen_stats_wo_punct(),
                        'pos_stat_table': tp.pos_freq(),
                        'pos_stat_graph_uses': tp.pos_freq_graph(),
                        'pos_stat_graph_words': tp.pos_freq_graph(use_tokens=False),
                        'omon_stat_table': tp.omon_freq(10),
                        'omon_stat_table_wo_stopwords': tp.omon_freq(10, include_stopwords=False),
                        'case_analysis_table': tp.case_analysis_table(),
                        'case_analysis_graph_nouns': tp.case_analysis_graph_nouns(),
                        'case_analysis_graph_adjs': tp.case_analysis_graph_adjs(),
                        'case_analysis_graph_sum': tp.case_analysis_graph_sum(),
                        'verb_forms_analysis_tense_table': tp.verb_form_analysis_tense_table(),
                        'verb_forms_analysis_person_table': tp.verb_form_analysis_person_table(),
                        'verb_forms_analysis_number_table': tp.verb_form_analysis_number_table(),
                        })


@app.route('/morph')
def morph():
    try:
        text = tuple(request.args.items())[0][0]
    except IndexError:
        return jsonify({'info_field': 'Пожалуйста, введите текст'})
    else:
        tp = HtmlTP(text)
        return jsonify({'morph_analysis_table': tp.morhp_analysis(include_punct=True)})


@app.route('/summary')
def summary():
    try:
        text = tuple(request.args.items())[0][0]
    except IndexError:
        return jsonify({'info_field': 'Пожалуйста, введите текст'})
    else:
        tp = HtmlTP(text)
        return jsonify({'summ_text': tp.summary()})


if __name__ == '__main__':
    app.run()
