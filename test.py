

import time
import cv2
from imutils.video import VideoStream
import requests
import json
import threading, time, queue
from flask import Flask, render_template, Response
from google.cloud.vision import types


# initialize the video stream
# vs = VideoStream(src=src).start()

camera = cv2.VideoCapture(0)

# warmup
time.sleep(2.0)

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

DENSE_CAP_API_KEY= "d946d749-f736-4643-b27f-502661cb7b7f"

def get_captions():

	flag, encodedImage = camera.read()
	file_name = 'image.jpg'
	cv2.imwrite(file_name, encodedImage)
	# file_name = 'https://cdnph.upi.com/svc/sv/upi/5711585753629/2020/1/8a65ca6bc7a15003a9b698a5d7788d0b/Wimbledon-tennis-tournament-canceled-2021-dates-announced.jpg'

	r = requests.post(
		"https://api.deepai.org/api/densecap", 
		files={ 'image': file_name }, 
		headers={'api-key': DENSE_CAP_API_KEY})
    
	result=r.json()
	print(result)
	picture_captions=set()
	for caption_dict in result['output']['captions']:
		if caption_dict['confidence']>0.9:
			picture_captions.add(caption_dict['caption'])

	picture_captions_li=list(picture_captions)

	for i in range(len(picture_captions_li)):
		for j in range(i+1,len(picture_captions_li)):
			str1=picture_captions_li[i]
			str2=picture_captions_li[j]
			if get_jaccard_sim(str1, str2) >0.4:
				picture_captions.remove(str1)

	return list(picture_captions)

def get_jaccard_sim(str1, str2): 
    a = set(str1.split()) 
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

def text_transformer():
	global camera, data, lock

	while True:

	
		description = get_captions()
		print(description)
		for text in description:
			# mimicking computation time
			print('arrive-lock')

			time.sleep(4)
			with lock:
				data.put(text)
				print('lock')

@app.route("/text_feed")
def text_feed():
	def generate():
		global data, lock

		while True:
			time.sleep(4)
			print('arrive-release')
			with lock:
				print('release')
				if data is None: continue
				scene = { "time": 0.0000000000000000, "text": data.get() }
			yield f"data: {scene}\n\n"

	return Response(generate(), mimetype = "text/event-stream")


if __name__ == '__main__':

	t = threading.Thread(target=text_transformer)
	t.daemon = True
	t.start()

	app.run(host="0.0.0.0", port="8000", debug=True, use_reloader=False)

# release the video stream pointer
# vs.stop()


# description = ['a person standing', 'a man is wearing a white shirt', 'a tennis court', 'a man is playing tennis', 'the tennis court is green', 'the head of a man', 'a white shirt', 'the people are watching the game', 'a white shoe', 'the crowd of the tennis match', 'a person is standing', 'a white chair', 'the reflection of the window', 'a green and white sign', 'the crowd of the people', 'the tennis court is green', 'the shoe is white', 'the people are green', 'the window is white', 'a man holding a racket']

