from flask import Flask
from flask import render_template, request
from query_processor import search_query
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if 'search_form' in request.form:
            if request.form['search']:
                query = request.form['search']
            singers = search_query(query)
        return render_template('index.html', query=query, singers=singers)

    return render_template('index.html', query='', singers=[])

if __name__ == "__main__":
    app.run(debug=True)