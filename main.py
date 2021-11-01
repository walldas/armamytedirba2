import time,pickle,os,ephem
from flask import Flask, render_template, url_for, request, redirect,make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime#,date

memory = "data.pickle"
	
def add_moon_phases(days):

	date = datetime.now()
	
	f =  [1,ephem.next_full_moon(date).triple()[1],int(ephem.next_full_moon(date).triple()[2])]
	f2 = [1,ephem.previous_full_moon(date).triple()[1],int(ephem.previous_full_moon(date).triple()[2])]
	p =  [2,ephem.next_first_quarter_moon(date).triple()[1],int(ephem.next_first_quarter_moon(date).triple()[2])]
	p2 = [2,ephem.previous_first_quarter_moon(date).triple()[1],int(ephem.previous_first_quarter_moon(date).triple()[2])]
	j =  [3,ephem.next_new_moon(date).triple()[1],int(ephem.next_new_moon(date).triple()[2])]
	j2 = [3,ephem.previous_new_moon(date).triple()[1],int(ephem.previous_new_moon(date).triple()[2])]
	d =  [4,ephem.next_last_quarter_moon(date).triple()[1],int(ephem.next_last_quarter_moon(date).triple()[2])]
	d2 = [4,ephem.previous_last_quarter_moon(date).triple()[1],int(ephem.previous_last_quarter_moon(date).triple()[2])]
	moon_phases = [p,f,d,j,p2,f2,d2,j2]
	
	for moon in moon_phases:
		for day in days:
			if day[1] == moon[2] and day[3] == moon[1]:
				if moon[0]>0:
					day[4] = moon[0]
				break
				
def save_pickle(any_data,file_ = "data.pickle"):
	with open(file_, 'wb') as f:
		pickle.dump(any_data, f, pickle.HIGHEST_PROTOCOL)

def load_pickle(file_):	
	if os.path.exists(file_):
		with open(file_, 'rb') as f:
			return pickle.load(f)
	return []
	
def calcEasterDate():
	dd = int(time.time())
	year = int(datetime.fromtimestamp(dd).strftime('%y'))+2000
	special_years = ['1954', '1981', '2049', '2076']
	specyr_sub = 7
	a = year % 19
	b = year % 4
	c = year % 7
	d = (19 * a + 24) % 30
	e = ((2 * b) + (4 * c) + (6 * d) + 5) % 7
	if year in special_years:
		dateofeaster = (22 + d + e) - specyr_sub
	else:
		dateofeaster = 22 + d + e
	if dateofeaster > 31:
		return [4, dateofeaster - 31]
	else:
		return [3, dateofeaster]
		
		
def add_no_work(days):
	no_work_days = [ [1,1], [2,16], [3,11], [5,1], [6,24], [7,6], [8,15], [11,1], [11,2], [12,24], [12,25], [12,26]]
	no_work_days.append(calcEasterDate())
	#prideti motinos diena pirmasis geguzes sekmadienis
	#prideti tevo diena pirmasis birzelio sekmadienis
	for no_work_day in no_work_days:
		for day in days:
			if day[1] == no_work_day[1] and day[3] == no_work_day[0]:
				day[5] = 1
				break
	
	
def i_to_state(i):
	return ["antra naktinė", " pirma laisva", "antra laisva", "trečia laisva", "pirma dieninė","antra dieninė", "laisva diena", "pirma naktinė"][i] 
	
def i_to_color(i):
	return [(255,0,0), (166,255,77), (77,255,77), (51,255,51), (210,255,77), (255,210,77), (255,153,51), (255,77,77)][i]
	
def i_to_border_color(i):
	a=[1,1,0,2,2,0,0,0][i]
	return [(0,255,0,0),(255,255,255,1),(0,0,0,1)][a]

def get_curent_next_month():
	curent_month = int(format(datetime.now()).split("-")[1])
	next_month = curent_month+1
	if curent_month ==12:
		next_month = 1
	return [curent_month,next_month]
	
def get_user_work_days():
	if os.path.exists(memory):
		return load_pickle(memory)
	year = {}
	for m in range(1,13,1):
		days = {}
		for d in range(1,32,1):
			days[d]= ""
		year[m]= days
	save_pickle(year,memory)
	return year
	
def to_table():
	days = []
	user_work_days = get_user_work_days()
	for d in range(0,29,1):
		dd = int(time.time() + d * 60 * 60 * 24)
		day = int(datetime.fromtimestamp(dd).strftime('%d'))
		month = int(datetime.fromtimestamp(dd).strftime('%m'))
		week= datetime.fromtimestamp(dd).isoweekday() - 1
		i = dd // (60 * 60 * 24) % 8
		moon = ""
		no_work_day = ""
		days.append([week, day, i_to_border_color(i),month, moon, no_work_day,user_work_days[month][day]])
	add_moon_phases(days)
	add_no_work(days)
	weeks = []
	week =[]
	[week.append([wk,"",(0,255,0,0)]) for wk in range(days[0][0])]
	for day in days:
		if not len(week) == 7:
			week.append(day)
		else:
			weeks.append(week)
			week = [day]
	# if not len(week) == 7:
		# weeks.append(week)
	n_weeks = []
	n_week=[]
	wkdays = ["P","A","T","K","Pe","Š","S"]
	wkdays = [[0,wk,(0,255,0,0)] for wk in wkdays]
	i = 0
	while i <7:
		n_week.append(wkdays[i])
		for week in weeks:
			n_week.append(week[i])
		n_weeks.append(n_week)
		n_week=[]
		i+=1
		
	return n_weeks
	
	
def work():
	h = 2 *60*60
	i = ( int(time.time()) + (h*60*60) ) // (60 * 60 * 24) % 8
	return(i_to_state(i), i_to_color(i))



app = Flask(__name__)

@app.route("/")
def index():
	weeks = to_table()
	state, color = work()
	return render_template("base.html",w_state=state,w_color=color,weeks=weeks)

@app.route("/i/",  methods=["POST","GET"])	
def add_user_work_days():
	curent_next_month = get_curent_next_month()

	if request.method == 'POST':
		year = get_user_work_days()
		for month in year:
			for day in year[month]:
				if month == curent_next_month[0] or month == curent_next_month[1]:
					cb = request.form.get("cb{}_{}".format(month,day))
					if cb == "on":
						year[month][day]= "checked"
					else:
						year[month][day]= ""
		
		save_pickle(year,memory)
		return redirect("/")
	else:
		year = get_user_work_days()
		return render_template("add_days.html",year=year,need_month=curent_next_month)
	
@app.errorhandler(404)
def not_found(e):
	return index()


if __name__=="__main__":
	app.run(debug=1, host="0.0.0.0", port=5000 , threaded=True)

