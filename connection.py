import mysql.connector
def connection_database():
	conn=mysql.connector.connect(user='root',password='',host='localhost',database='fingerdb')       # connect to MySql database
	cur=conn.cursor()
	return conn,cur


connection_database()