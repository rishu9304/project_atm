import time
from sinchsms import SinchSMS

number = '+917001354181'
message = 'I love SMS!'

client = SinchSMS('7d4d335a8f924bb3903427b74355a0a1','f5cce5c3f91e4feba2df74a31ffb4bd3')
print("Sending '%s' to %s" % (message, number))
response = client.send_message(number, message)
message_id = response['messageId']

response = client.check_status(message_id)
while response['status'] != 'Successful':
    print(response['status'])
    time.sleep(1)
    response = client.check_status(message_id)
    print(response['status'])