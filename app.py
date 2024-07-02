from datetime import datetime
from datetime import timezone
import requests, time, json

endpoint_record = "https://my.sirius.online/api/activity/v0/schedule/student/record"
endpoint_subscribe = "https://my.sirius.online/api/activity/v0/schedule/student/record/subscribe"
headers = {"Authorization":"Bearer ",
        'Content-type':'application/json', 
        'Accept':'application/json'}
now = datetime.now().astimezone(timezone.utc)
today8am = now.replace(hour=20, minute=45, second=0, microsecond=0)

r = requests.get(endpoint_record, headers=headers).json()
events = r['success']
eventlist = []
index = 0
for day in events:
    print(day['dayISO'] + ":")
    for event in day['events']:
        datetime_object = datetime.fromisoformat(event['recordStart'])
        availability = ""

        if(not event['availability']['isAvailable'] or int(event['peopleMax']) == int(event['peopleCurrent'])): availability = "ЗАПИСЬ НЕ ДОСТУПНА. "
        print(str(index) + ". " + availability + event['eventName'] + "; Запись открывается в " + str(datetime_object))
        elem = {
            'id': index,
            'eventId': event['eventId'],
            'name': event['eventName'],
            'subscribe_time': datetime_object
        }
        eventlist.append(elem)
        index += 1
    print('\n')

choise = int(input('Выберите ивент для записи: '))
chosenEvent = eventlist[choise]
data = json.dumps({"eventId":chosenEvent['eventId']})

print('Ожидаем начала записи...')
while(1 == 1):
    now = datetime.now().astimezone(timezone.utc)
    if(now >= chosenEvent['subscribe_time']):
            r = requests.post(endpoint_subscribe, data=data, headers=headers)
            if(r.ok and not "error" in r.json()): print('Запись проведена успешно')
            else: print('При записи произошла ошибка, возможно мест не осталось')
            break
    else: 
          time.sleep(0.01)