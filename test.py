from datetime import datetime
# ['Sun', 'Oct', '27', '23:08:24', '2019']
t = "Tue, 12 Jun 2018 09:55:22"
t2 ='Thu, 16 Dec 2010 12:14:05'

date = datetime.now().strftime("%c").split(" ")
print(type(datetime.now()))
print(date)
newDate = date[0] + ', ' + date[2] + " " + date[1] + " " +date[4] + " " + date[3]
date = datetime.strptime(newDate, '%a, %d %b %Y %H:%M:%S')
print(date.isoformat())