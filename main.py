import threading, time, queue
from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/camera")
def camera():
	return render_template("camera.html")

@app.route("/map")
def map():
	return render_template("map.html")

data = queue.Queue()
lock = threading.Lock()

def text_transformer():
	global data, lock
	description = ['a person standing', 'a man is wearing a white shirt', 'a tennis court', 'a man is playing tennis', 'the tennis court is green', 'the head of a man', 'a white shirt', 'the people are watching the game', 'a white shoe', 'the crowd of the tennis match', 'a person is standing', 'a white chair', 'the reflection of the window', 'a green and white sign', 'the crowd of the people', 'the tennis court is green', 'the shoe is white', 'the people are green', 'the window is white', 'a man holding a racket']
	for text in description:
		# mimicking computation time
		time.sleep(5)
		with lock:
			data.put(text)

@app.route("/text_feed")
def text_feed():
	def generate():
		global data, lock

		while True:
			time.sleep(5)
			with lock:
				if data is None: continue
				scene = { "time": 0.0000000000000000, "text": data.get() }
			yield f"data: {scene}\n\n"

	return Response(generate(), mimetype = "text/event-stream")


if __name__ == '__main__':

	t = threading.Thread(target=text_transformer)
	t.daemon = True
	t.start()

	app.run(host="0.0.0.0", port="8000", debug=True, use_reloader=False)
