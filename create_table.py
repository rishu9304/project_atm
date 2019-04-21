from connection import connection_database

conn,cur = connection_database()

#cur.execute("drop table if exists fingertb")

#cur.execute("create table fingertb(id int primary key,name varchar(20),mobile varchar(13),account_no varchar(15),balance varchar(10))")
#print("created table sucessfully!!")

cur.execute("drop table if exists transaction")
cur.execute("create table transaction(id int,balance varchar(10),balance_withdraw varchar(10),withdraw_data varchar(10))")