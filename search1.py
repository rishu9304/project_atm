import serial
import time
import struct,sys
from connection import connection_database

conn,cur = connection_database()

ser = serial.Serial('COM7',57600)
pack = [0xef01, 0xffffffff, 0x1]

def printx():
    for i in l:
        print(i)
    print( '')

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

def search():
    data = [0x4, 0x1, 0x0, 0x0, 0x0, 0x5]
    writePacket(data)
    s = readPacket()
    return s[4:-1]  

def mainfuncn():
    if verifyFinger():
        print( 'Verification Error')
        sys.exit(-1)

    print('Put finger')
    sys.stdout.flush()

    time.sleep(1)   
    for _ in range(5):
        g = genImg()
        if g == 0:
            break
        #time.sleep(1)

        print( '.')
        sys.stdout.flush()

    print( '')
    sys.stdout.flush()
    if g != 0:
        sys.exit(-1)

    if img2Tz(1):
        print('Conversion Error')
        sys.exit(-1)

    r = search()
    if r[0]==0:
        print('Search result', r)
        ids = str(r[2])
        print("su")
        query = "select * from fingertb where id = %s"
        cur.execute(query,(ids,))
        res = cur.fetchone()
        print("Name of the customer: ",res[1])
        sys.exit(0)
    else:
        print("user is not registered")

mainfuncn()