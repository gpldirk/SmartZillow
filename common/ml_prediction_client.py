import pyjsonrpc

URL = 'http://localhost:5050'

client = pyjsonrpc.HttpClient(url=URL)

def predict(zipcode, property_type, bedroom, bathroom, size):
	predicted_value = client.call('predict', zipcode, property_type, bedroom, bathroom, size)
	return predicted_value