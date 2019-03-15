from cloudAMQP_client import CloudAMQPClient

CLOUDAMQP_URL = 'amqp://dmsrypxa:H_jp8yHat9_x35fXpn3tlQMUNkRu-xf1@caterpillar.rmq.cloudamqp.com/dmsrypxa'
QUEUE_NAME = 'dataFetcherTaskQueue'

# Initialize a client
client = CloudAMQPClient(CLOUDAMQP_URL, QUEUE_NAME)

# Send a message
#client.sendDataFetcherTask({'name' : 'test message'})


# Receive a message
client.getDataFetcherTask()
