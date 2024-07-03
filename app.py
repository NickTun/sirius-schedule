from datetime import datetime
from datetime import timezone
import requests, time, json
from urllib.parse import urlparse
from urllib.parse import parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

endpoint_record = "https://my.sirius.online/api/activity/v0/schedule/student/record"
endpoint_subscribe = "https://my.sirius.online/api/activity/v0/schedule/student/record/subscribe"

login = input("Введите электронную почту: ")
password = input("Введите пароль: ")

print('Обработка данных...')

driver.get("https://auth.sirius.online")
driver.find_element(By.XPATH, "//*[text()[contains(., 'По паролю')]]").click()
driver.find_element("name", "email").send_keys(login)
driver.find_element("name", "password").send_keys(password)
driver.find_element(By.XPATH, "//*[text()[contains(., 'Войти')]]").click()

time.sleep(15)

token = driver.execute_script("return window.localStorage;")['AuthToken']

driver.quit()

headers = {
    'Authorization': 'Bearer ' + token,
    'Content-type':'application/json', 
    'Accept':'application/json'
}

record = requests.get(endpoint_record, headers=headers).json()
events = record['success']
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