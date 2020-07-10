#with mongodb
from fastapi import FastAPI,Query 
import uvicorn 
from pymongo import MongoClient            
import re



myclient = MongoClient('localhost',27017)
mydb = myclient["taskAssignment"] #db name
mycoll=mydb["testdemo"] # collection name  like tables in sql



#init app
app=FastAPI()



#http://127.0.0.1:8000/
@app.get('/')
async def index():
	return {"text":"I m  Anmoljeet Singh wadali"}

#add task
#duedate--> dd/mm/yy
#http://127.0.0.1:8000/task/add?name=xxx&duedate=01/12/2020
@app.get('/task/add')
async def add(name:str= Query(None),duedate:str= Query(None)):
	name=name.lower()
	myquery={"Name":name}
	datecheck=date_validate(duedate)
	if datecheck==None:
		return {"Error":"Date is not proper format kindly Check it","Allowed Format":"dd/mm/yy"}

	if mycoll.find_one(myquery)==None:
		task={"Name":name, "DueDate":duedate,"Complete":False}
		mycoll.insert_one(task)
		return {"Status":"Task is added!!!","Task name":name,"Due Date":duedate}
	else:
		return {"Status":"Task Cannot Be added as Task with this name Already Exits!!! Task Name needs To be Unique"}


#delete task
#http://127.0.0.1:8000/task/delete?name=xxx
@app.get('/task/delete')
async def delete(name:str= Query(None)):
	myquery={"Name":name}
	if mycoll.find_one(myquery)!=None:
		mycoll.delete_one(myquery) 
		return {"Result":"Task is Deleted From DataBase"}
	else:
		return {"Warning":"No task with This name Exist in DataBase!!!"}
    




#update task
#1 make the task complete
#http://127.0.0.1:8000/task/update/complete?name=anmol
@app.get('/task/update/complete')
async def updatecomplete(name:str= Query(None)):
        name=name.lower()
        myquery={"Name":name}
        result=mycoll.find_one(myquery)
        if result!=None:
            result['Complete']=not result['Complete']
            newvalues = { "$set":result }
            mycoll.update_one(myquery, newvalues)#update single query/record
            if result['Complete']==True:
            	Status="Task is Completed"
            else:
            	Status="Task is InCompleted"


            return {"Result":"Completion Status Updated","Task Status":Status}
        else:
            return {"Warning":"No task with This name Exist in DataBase!!!"}

#2 update due date
#http://127.0.0.1:8000/task/update/duedate?name=anmol&newduedate=11/12/21
@app.get('/task/update/duedate')
async def updateduedate(name:str= Query(None),newduedate:str= Query(None)):
        name=name.lower()
        myquery={"Name":name}
        datecheck=date_validate(newduedate)
        if datecheck==None:
        	return {"Error":"Date is not in proper format kindly Check it","Allowed Format":"dd/mm/yy"}
        result=mycoll.find_one(myquery)
        if result!=None:
            olddate=result['DueDate']
            result['DueDate']=newduedate
            newvalues = { "$set":result }
            mycoll.update_one(myquery, newvalues)#update single query/record
            return {"Status":"Due Date Updated Successfully from {} to {} ".format(olddate,newduedate)}
        else:
            return {"Warning":"No task with This name Exist in DataBase!!!"}
            

# view a task
#http://127.0.0.1:8000/task/view?name=xxx
@app.get('/task/view')
async def view(name:str= Query(None)):
    name=name.lower()
    myquery={"Name":name}
    result=mycoll.find_one(myquery)
    if result!=None:
        ans=result
        ans.pop('_id')
        return ans
    else:
        return {"Warning":"No task with This name Exist in DataBase!!!"}



def email_vaildate(eid):
    email_regex = re.compile(r"[\w\.-]+@[\w\.-]+")
    result = email_regex.findall(eid)
    if len(result)==0:
        return None
    return result[0]
def date_validate(date):
    #format dd/mm/yy
    regex= re.compile(r"[\d{2}]+/[\d{2}]+/[\d{2}]+")
    result1=regex.findall(date)
    if len(result1)==0:
        return None
    regex2=re.compile(r'(\d{2})/(\d{2})/(\d{2})')
    result2=regex2.findall(result1[0])
    dd=int(result2[0][0])
    mm=int(result2[0][1])
    yy=int(result2[0][2])
    if (dd>=1 and dd<=31) and (mm>=1 and mm<=12):
        return result1[0]
    else:
        return None
        
    

#Share task with another user using their email (Only view access)
#http://127.0.0.1:8000/task/share?name=anmol&emailid=anmolwadali1998@gmail.com
@app.get('/task/share')
async def share(name:str= Query(None),eid:str= Query(None)):
	name=name.lower()
	myquery={"Name":name}
	result=mycoll.find_one(myquery)
	emailcheck=email_vaildate(eid)
	print(result)
	if result!=None and emailcheck!=None:
		ans=result
		ans.pop('_id')
		return {"Result":"Task is Shared Successfully with User using Emailid","Email Id":eid,"Task details":ans}
	else:
		return {"Warning":"No task with This name Exist in DataBase/ Invalid Email Plz try Again!!!"}


if __name__ == '__main__':
	uvicorn.run(app,port=8000)