import serial
import time
import struct,sys
from connection import connection_database


conn,cur = connection_database()

ser = serial.Serial(port='COM7', baudrate=57600)
pack = [0xef01, 0xffffffff, 0x1]

def printx(l):
    for i in l:
        print (i)
    print ('')

def readPacket():
    time.sleep(1)
    w = ser.inWaiting()
    ret = []
    if w >= 9:
        s = ser.read(9) #partial read to get length
        ret.extend(struct.unpack('!HIBH', s))
        ln = ret[-1]

        time.sleep(1)
        w = ser.inWaiting()
        if w >= ln:
            s = ser.read(ln)
            form = '!' + 'B' * (ln - 2) + 'H'
            ret.extend(struct.unpack(form, s))
    return ret


def writePacket(data):
    pack2 = pack + [(len(data) + 2)]
    a = sum(pack2[-2:] + data)
    pack_str = '!HIBH' + 'B' * len(data) + 'H'
    l = pack2 + data + [a]
    s = struct.pack(pack_str, *l)
    ser.write(s)


def verifyFinger():
    data = [0x13, 0x0, 0, 0, 0]
    writePacket(data)
    s = readPacket()
    return s[4]

def genImg():
    data = [0x1]
    writePacket(data)
    s = readPacket()
    return s[4] 

def img2Tz(buf):
    data = [0x2, buf]
    writePacket(data)
    s = readPacket()
    return s[4]

def regModel():
    data = [0x5]
    writePacket(data)
    s = readPacket()
    return s[4]

def store(id):
    data = [0x6, 0x1, 0x0, id]
    writePacket(data)
    s = readPacket()
    return s[4] 

name = raw_input("enter customer name: ")
mobile = raw_input("enter customer mobile number: ")
account_no = raw_input("enter customer account number: ")
balance =  raw_input("enter opening balance of customer: ")


if verifyFinger():
    print ('Verification Error')
    sys.exit(0)

print ('Put finger')
sys.stdout.flush()

time.sleep(1)   
while genImg():
    time.sleep(0.1)

    print ('.')
    sys.stdout.flush()

print ('')
sys.stdout.flush()

if img2Tz(1):
    print ('Conversion Error')
    sys.exit(0)

print ('Put finger again')
sys.stdout.flush()

time.sleep(1)   
while genImg():
    time.sleep(0.1)
    print ('.')
    sys.stdout.flush()

print ('')
sys.stdout.flush()

if img2Tz(2):
    print ('Conversion Error')
    sys.exit(0)

if regModel():
    print ('Template Error')
    sys.exit(0)

query = "select count(id) from fingertb"
cur.execute(query)
res = cur.fetchone()
print(res)
id = res[0]+1


if store(id):
    print('Store Error')
    sys.exit(0) 

query =  "insert into fingertb(id,name,mobile,account_no,balance)values(%s,%s,%s,%s,%s)"
cur.execute(query,(str(id),name,mobile,account_no,balance))
conn.commit()

print ("Enrolled successfully at id %d"%id)
