from __future__ import print_function
from flask import Flask, json, jsonify, abort, make_response, request, url_for
from flask_cors import CORS
from datetime import datetime
from flask import render_template
import operator
import sys
import pymysql
import pymysql.cursors
import requests
import _thread

app = Flask(__name__)
CORS(app)

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

dbUsername = 'root'
dbPassword = 'root'

databaseConnection = pymysql.connect(
	host='localhost',
	port=3306,
	user=dbUsername,
	password=dbPassword,
	db='IoTUseCase',
	charset='utf8',
	cursorclass=pymysql.cursors.DictCursor,
	autocommit=True
)

successMessage = {
	"status": "success",
	"message": ""
}

@app.after_request
def add_header(r):
	""" Disable caching """
	r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
	r.headers["Pragma"] = "no-cache"
	r.headers["Expires"] = "0"
	return r

@app.route('/api/meta', methods=['POST'])
def addMeta():
	"""Add sensor node metadata to the database before accepting sensor data from it."""

	fields = ["nodeName", "sensors"]

	if not request.json:
		abort(400)

	if not sorted(request.json.keys()) == sorted(fields):
		abort(400)

	if not request.json["sensors"]:
		abort(400)

	nodeName = request.json["nodeName"]

	databaseCursor = databaseConnection.cursor()

	query = """
		SELECT MAX(nodeId) 
		FROM SensorMeta;
	"""
	databaseCursor.execute(query)
	res = databaseCursor.fetchone()

	result = res["MAX(nodeId)"]
	if result is None:
		result = 0
	print(result, type(result))

	nextId = int(result) + 1

	query = """INSERT INTO SensorMeta (nodeId, nodeName, sensorId, sensorName) VALUES"""
	for k,v in request.json["sensors"].items():
		query += """ ({}, '{}', {}, '{}'),""".format(str(nextId), str(nodeName), str(k), str(v))
	query = query[:-1] + ";"

	databaseCursor.execute(query)

	respData = {
		"status": "success",
		"data": {
			"nodeId": nextId,
			"nodeName": nodeName
		}
	}

	response = app.response_class(
		response = json.dumps(respData),
		status = 200,
		mimetype = 'application/json'
	)
	return response

@app.route('/api/meta/node/<string:nodeId>', methods=['GET'])
def getNodeMeta(nodeId):
	"""View metadata of given sensor node."""

	respData = {
		"data": {}
	}

	databaseCursor = databaseConnection.cursor()

	query = """
		SELECT nodeId,nodeName,sensorId,sensorName
		FROM SensorMeta
		WHERE nodeId = {};
	""".format(str(nodeId))
	databaseCursor.execute(query)
	res = databaseCursor.fetchall()
	print(res, type(res))

	if not res:
		abort(404)

	respData["data"]["nodeId"] = nodeId
	respData["data"]["nodeName"] = res[0]["nodeName"]
	respData["data"]["sensors"] = {}
	for row in res:
		respData["data"]["sensors"][row["sensorId"]] = row["sensorName"]

	response = app.response_class(
		response = json.dumps(respData),
		status = 200,
		mimetype = 'application/json'
	)
	return response

@app.route('/api/meta/node/<string:nodeId>/sensor/<string:sensorId>', methods=['GET'])
def getSensorMeta(nodeId, sensorId):
	"""View metadata of given sensor in given sensor node."""

	respData = {
		"data": {}
	}

	databaseCursor = databaseConnection.cursor()

	query = """
		SELECT nodeId,nodeName,sensorId,sensorName
		FROM SensorMeta
		WHERE nodeId = {} AND sensorId = {};
	""".format(str(nodeId), str(sensorId))
	databaseCursor.execute(query)
	res = databaseCursor.fetchone()
	print(res, type(res))

	if res is None:
		abort(404)

	respData["data"]["nodeId"] = nodeId
	respData["data"]["nodeName"] = res["nodeName"]
	respData["data"]["sensorId"] = res["sensorId"]
	respData["data"]["sensorName"] = res["sensorName"]

	response = app.response_class(
		response = json.dumps(respData),
		status = 200,
		mimetype = 'application/json'
	)
	return response


def updateRollingAverage(url, sensorData):
	"""Helper function to offload task to worker role."""
	resp = requests.post(url, json=sensorData)
	return

@app.route('/api/data', methods=['POST'])
def addData():
	"""Add sensor node data to the database."""

	fields = ["nodeId", "sensorData"]

	if not request.json:
		abort(400)

	if not sorted(request.json.keys()) == sorted(fields):
		abort(400)

	if not request.json["sensorData"]:
		abort(400)

	nodeId = request.json["nodeId"]

	databaseCursor = databaseConnection.cursor()

	query = """INSERT INTO SensorData (nodeId, sensorId, dataValue) VALUES"""
	for k,v in request.json["sensorData"].items():
		query += """ ({}, {}, {}),""".format(str(nodeId), str(k), str(v))
	query = query[:-1] + ";"

	databaseCursor.execute(query)

	url = "http://localhost:5001/api/rollingaverage/node/{}".format(nodeId)

	try:
		t = threading.Thread(target=updateRollingAverage, args=(url, request.json["sensorData"],))
		t.start()
	except:
		print("Error: unable to start thread")

	response = app.response_class(
		response = json.dumps(successMessage),
		status = 200,
		mimetype = 'application/json'
	)
	return response

@app.route('/api/data/node/<string:nodeId>/sensor/<string:sensorId>/latest', methods=['GET'])
def getData(nodeId, sensorId):
	"""View latest data value for given sensor in given sensor node."""

	respData = {
		"data": {}
	}
	
	databaseCursor = databaseConnection.cursor()

	query = """
		SELECT seqId, nodeId, sensorId, dataValue
		FROM SensorData
		WHERE nodeId = {} AND sensorId = {}
        ORDER BY seqId DESC
        LIMIT 1;
	""".format(str(nodeId), str(sensorId))
	databaseCursor.execute(query)
	res = databaseCursor.fetchone()
	print(res, type(res))

	if res is None:
		abort(404)

	respData["data"]["nodeId"] = nodeId
	respData["data"]["sensorId"] = sensorId
	respData["data"]["seqId"] = res["seqId"]
	respData["data"]["dataValue"] = res["dataValue"]

	response = app.response_class(
		response = json.dumps(respData),
		status = 200,
		mimetype = 'application/json'
	)
	return response

@app.route('/api/rollingaverage/node/<string:nodeId>/sensor/<string:sensorId>', methods=['GET'])
def getRollingAverage(nodeId, sensorId):
	"""View rolling average of data values for given sensor in given sensor node."""

	url = "http://localhost:5001/api/rollingaverage/node/{}/sensor/{}".format(nodeId, sensorId)
	resp = requests.get(url)

	respData = resp.json()
	print(respData, type(respData))

	response = app.response_class(
		response = json.dumps(respData),
		status = 200,
		mimetype = 'application/json'
	)
	return response


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
@app.route('/index', methods=['GET'])
def showHomepage():
	return render_template(
		'index.html',
		title='Home',
		year=datetime.now().year,
		message='home.'
	)


@app.route('/graph/node/<string:nodeId>/sensor/<string:sensorId>', methods=['GET'])
def showGraph():
	return render_template(
		'index.html',
		title='Graph',
		year=datetime.now().year,
		message='graph.'
	)


if __name__ == '__main__':
	app.run(threaded=True, debug=True, host='localhost', port=5000)