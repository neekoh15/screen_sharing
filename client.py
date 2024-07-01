
from flask import Flask, render_template

app = Flask(__name__)
HOST = '0.0.0.0'
PORT = 5000

@app.route('/')
def main():
    return render_template('index.html')

# main driver function
if __name__ == '__main__':
    app.run(host=HOST, port=PORT, threaded=True)
