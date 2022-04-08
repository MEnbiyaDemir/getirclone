import zmq
import csv
import datetime as dt
from datetime import timedelta




project_date = "2018-10-02 17:06"
old_date = dt.datetime.now()
current_date=dt.datetime.now()
bir_kere_calis_flag = 0
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5560")




while True:
    message = socket.recv()
    #read csv, and split on "," the line
    #csv_file = csv.reader(open('allCars.csv', "r"), delimiter=",")
    f = open('allCars.csv', "r")
    csv_file = csv.reader(f, delimiter=',')
 

    new_list = []
    
    
    if(bir_kere_calis_flag == 0):
        bir_kere_calis_flag = 1
        old_date = dt.datetime.now()
        
    current_date=dt.datetime.now()
    print("zaman farki: "+str((current_date-old_date).total_seconds()) )    
    
    if((current_date-old_date).total_seconds() >= 10):
        #1dk arttır
        date_time_obj = dt.datetime.strptime(project_date, '%Y-%m-%d %H:%M')
        final_time = date_time_obj + timedelta(minutes=1)
        final_time_str = final_time.strftime('%Y-%m-%d %H:%M')
        project_date = final_time_str
        old_date = current_date


    print(project_date) 
    
    
    latitude = ''
    longitude = ''
    id = str(message).replace('b','').replace('\'','')
    print(f"Car id: {id}")
    for row in csv_file:
        if project_date in row and id in row :
            #print ('x:' + row[1] + ', y:' + row[2])
            latitude = str(row[1])
            longitude = str(row[2])
            break

    print(latitude +','+ longitude)    
    print("--------------------------")
    xxxx = str(project_date)
    f.close()    
    socket.send_string(f"{latitude} {longitude} {xxxx}")
    