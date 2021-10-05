from bs4 import BeautifulSoup
import requests
import datetime
import json
from dataclasses import dataclass
import time

'''
Section 0: API set up
'''
response = requests.get('https://api.tomorrow.io/v4/timelines?location=-73.98529171943665,40.75872069597532&fields'
                        '=weatherCode&timesteps=1d&units=metric&apikey=t4YfOgzGiud1Ju72SGD3xwASuOlmaW3V')
APIdic = response.json()

# print(APIdic['data']['timelines'][0]['intervals']) contains the list of dictionaries that has the keys 'startTime'
# (i.e., the date) and 'values' (contains a dictionary with the single key value pair {'weatherCode': TheCode}

WeatherDateList = APIdic['data']['timelines'][0]['intervals']

# print(WeatherDateList)
# print(type(WeatherList)), list
# Now that we can get a list containing the date and weather I'm going to just add the dates to one list and the weather
# codes to another list.

WeatherCodeList = []
DateList = []
for i in WeatherDateList:
    DateList.append(i['startTime'])
    WeatherCodeList.append(i['values']['weatherCode'])

# print(WeatherCodeList)
# print(DateList)

# Now that we have those lists we just need to do some cleaning on the dates so that they can be put into datetime
# format and we have to translate the weather codes to things like 'sunny', 'cloudy', etc.
# Below is the for loop for translating the weather codes

WeatherCodeListTranslated = []

for i in range(len(WeatherCodeList)):
    if WeatherCodeList[i] == 0:
        WeatherCodeListTranslated.insert(i, "unknown")
    elif WeatherCodeList[i] == 1000:
        WeatherCodeListTranslated.insert(i, "clear")
    elif WeatherCodeList[i] == 1001:
        WeatherCodeListTranslated.insert(i, "cloudy")
    elif WeatherCodeList[i] == 1100:
        WeatherCodeListTranslated.insert(i, "mostly clear")
    elif WeatherCodeList[i] == 1101:
        WeatherCodeListTranslated.insert(i, "partially cloudy")
    elif WeatherCodeList[i] == 1102:
        WeatherCodeListTranslated.insert(i, "mostly cloudy")
    elif WeatherCodeList[i] == 2000:
        WeatherCodeListTranslated.insert(i, "fog")
    elif WeatherCodeList[i] == 2100:
        WeatherCodeListTranslated.insert(i, "light fog")
    elif WeatherCodeList[i] == 3000:
        WeatherCodeListTranslated.insert(i, "breezy")
    elif WeatherCodeList[i] == 3001:
        WeatherCodeListTranslated.insert(i, "windy")
    elif WeatherCodeList[i] == 3002:
        WeatherCodeListTranslated.insert(i, "strong wind")
    elif WeatherCodeList[i] == 4000:
        WeatherCodeListTranslated.insert(i, "Drizzle")

# print(WeatherCodeListTranslated)

DateListCleaned = []

for i in DateList:
    date = str(datetime.datetime.strptime(i[:10], "%Y-%m-%d").date())
    DateListCleaned.append(date)

# print(DateListCleaned)

# The for-loops above work, and I'll now put things back into a dictionary

CurrentWeatherDict = {}
for i in range(len(DateListCleaned)):
    CurrentWeatherDict[DateListCleaned[i]] = WeatherCodeListTranslated[i]

# print(CurrentWeatherDict)

'''
Section 1: Web-Scraping, and JSON 
(i.e., all of the parts necessary to grade the 'high-level requirements' section on the rubric is here, except for the 
API weather stuff)

In the section below I'll be scarping the 'timeanddate' website for the list of holidays and extracting them including
their date. At the end I'll use the originally provided JSON file to create a final list of holidays by adding the
scraped list to the list in the original JSON.
'''

with open(r'C:\Users\17733\OneDrive\Documents\holidays.json') as f:
    global OriginalHolidays
    OriginalHolidays = json.load(f)


def getHTML(url):  # Using function from lesson to extract the HTML for the page containing the holidays table
    response = requests.get(url)
    return response.text


HolidayHTML = getHTML('https://www.timeanddate.com/holidays/us/?hol=43122559')

# print(HolidayHTML), HTML is quite long and not easy to inspect directly on PyCharm.
# Therefore I went back to the webpage, inspected, and found that the table is in a 'table' tag with
# an attribute id = "holidays-table". Using these we have:

HolidaySoup = BeautifulSoup(HolidayHTML, 'html.parser')
HolidayTable = HolidaySoup.find('table', attrs={'id': 'holidays-table'})
HolidayTableNoHeaders = HolidayTable.find('tbody')
# print(HolidayTableNoHeaders) wanted to get rid of the header row from table as it was not needed

# For the base assessment we simply need the date and holiday name so I'll call the tags appropriately and use a
# for-loop to get all of the entries

ListOfHolidays = []

for row in HolidayTableNoHeaders.find_all_next('tr'):
    # print(row), used to check what I'm actually looping over.
    # print(row.find_next('th').get_text()) Used to verify that I'll get the date (month/day), however some
    # tags are empty (i.e., NoneType) hence my if-else statement below
    # print(row.find_next('a').get_text()), The <a> tag is the only one with the holiday name
    holiday = {}
    holiday['name'] = row.find_next('a').get_text()
    if row.find_next('th') is not None:
        holiday['date'] = row.find_next('th').get_text()
    ListOfHolidays.append(holiday)

# print(*ListOfHolidays, sep='\n') Some, duplicates and the last entry is not a holiday as evident by the name and lack
# of date
# print(len(ListOfHolidays)): 513 so definite duplicates, so I'm going to clean my list below

ListOfHolidaysCleaned = []

for i in ListOfHolidays:
    if i in ListOfHolidaysCleaned:
        pass
    else:
        ListOfHolidaysCleaned.append(i)
ListOfHolidaysCleaned.pop()  # last element was not a holiday and required removing

# print(*ListOfHolidaysCleaned, sep='\n'), did not see repeats :)
# print(len(ListOfHolidaysCleaned)): 472

# I still need to convert the date to yyyy-mm-dd format and will do so below:

for holiday in ListOfHolidaysCleaned:
    for k, v in holiday.items():
        if k == 'date':
            holiday[k] = v + " 2021"
    for k, v in holiday.items():
        if k == 'date':
            holiday[k] = str(datetime.datetime.strptime(v, "%b %d %Y").date())

# print(*ListOfHolidaysCleaned, sep='\n'), The for-loop worked :)

# Now that we have our web-scraped and cleaned data it's now time to join it to the original json and save the resulting
# dictionary to a new (updated) json file

FinalHolidayDict = OriginalHolidays

# print(type(OriginalHolidays)), double checking that it is a dictionary

for i in ListOfHolidaysCleaned:
    FinalHolidayDict["holidays"].append(i)

# print(*FinalHolidayList["holidays"], sep='\n'), for loop worked wonderfully :)
# Time for file creation :)
# now that we have all the holidays in the correct format it's time to make a JSON. Lets do it and view the results.

HolidayJSON = json.dumps(FinalHolidayDict, indent=2)
# print(HolidayJSON), my indent level looks good!

with open('AllHolidays.json', 'w') as f:
    f.write(HolidayJSON)

# The above code worked great! if you'd to see for yourself view the attached file in github.


'''
END of section 1
'''

'''
Section 2: Creation of my Holiday Class, and instantiation of all of the holidays in a list.
'''


@dataclass
class Holiday:
    name: str
    date: datetime.date

    def __str__(self):
        return self.name + ': ' + "(" + str(self.date) + ")"

    def __repr__(self):
        return 'DEBUGGING <%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self)))
# The purpose of the dunder method below is due to the fact that I use a set to keep track of my added holidays.
# However sets require hashs and therefore I defined mine below so that my class instances are hashable.
    def __hash__(self):
        return hash((self.name, self.date))


# with the holiday class created I will now instantiate the class using my 2021 list of holidays

Holidays2021bank = []

# print(*FinalHolidayDict['holidays'], sep='\n')

for i in FinalHolidayDict['holidays']:
    holiday_name = i['name']
    holiday_date = datetime.datetime.strptime(i['date'], '%Y-%m-%d').date()
    Holidays2021bank.append(Holiday(holiday_name, holiday_date))

# print(*Holidays2021bank, sep='\n') Looks good!
# print(len(Holidays2021bank)) Same number of holidays as original.
# print(type(Holidays2021bank[0])) is a holiday object!
# print(Holidays2021bank[0].date) printed date.
# print(type(Holidays2021bank[0].date)) datetime.date type as expected
# print(repr(Holidays2021bank[0])), dunder method for debugging shows correct output


'''
section 3: UI and their functionality 
'''

# Before saving, the set below is where all of the holidays are added/removed from. A set is used as it will not allow
# duplicates
TempAddedHolidays = set()

AddedHolidays = []  # once the save button is executed the elements from the set above are added to this list


def start_menu():
    print('''
Welcome to the Holiday Management system!
=========================================
There are %i holidays currently loaded into the system which can be added.
    ''' % len(Holidays2021bank))
    while True:
        choice = str(input('Would you like to enter the main-menu to view and/or add/remove from the current holiday '
                           'list? [y/n]:')).lower().strip()
        if choice == 'y' or choice == 'n':
            break
        else:
            print("Error: please input either 'y' or 'n'.")
    if choice == 'n':
        print('GoodBye!')
    else:
        main_menu()

def main_menu():
    print('''
Welcome to the main menu:   
=====================================|         
1. Add a Holiday                     |
2. Remove a Holiday                  |  
3. Save Holiday List                 |
4. View Holidays                     |
5. Exit                              |
=====================================|
    ''')
    while True:
        selection = str(input("Please select an option [1,2,3,4,5]:")).strip()
        if selection not in '12345':
            print('Please input a single number between 1 and 5')
        else:
            break
    if selection == '1':
        add_a_holiday()
    elif selection == '2':
        remove_a_holiday()
    elif selection == '3':
        save_holiday_list()
    elif selection == '4':
        view_holiday()
    else:
        if len(TempAddedHolidays) == 0:
            print('''
Exit
====
            ''')
            while True:
                choice = str(input("Are you sure you'd like to exit? [y/n]:")).strip().lower()
                if choice == 'y' or choice == 'n':
                    break
                else:
                    print('please give a valid input.')
            if choice == 'y':
                print('Goodbye!')
            else:
                main_menu()
        else:
            while True:
                choice = str(input("Are you sure you'd like to exit? Any unsaved changes will be lost. [y/n]:")).strip().lower()
                if choice == 'y' or choice == 'n':
                    break
                else:
                    print('please give a valid input.')
            if choice == 'y':
                print('Goodbye!')
            else:
                main_menu()

def add_a_holiday():
    print('''
Add a Holiday
=============
    ''')
    while True:
        HolidayName = str(input("Please input the holiday name (Alternatively, enter 'q' if you would no longer like"
                                " to enter a holiday name):"))
        HolidayNames = [i.name for i in Holidays2021bank]
        if HolidayName == 'q':
            break
        elif HolidayName not in HolidayNames:
            print("Either you've inputted the name incorrectly or this holiday is not in the list of loaded holidays."
                  "Either way please try again.")
        else:
            break
    if HolidayName == 'q':
        print('Returning to main.')
        main_menu()
    else:
        while True:
            try:
                HolidayDate = datetime.datetime.strptime(input('Please the date in yyyy-mm-dd format:'), '%Y-%m-%d').date()
            except:
                print('Invalid date or input format. Please try again.')
            for i in Holidays2021bank:
                if HolidayName == i.name:
                    TheDate = i.date
            if TheDate == HolidayDate:
                break
            else:
                print(
                    '''
    That is the incorrect date for that holiday. The date for %s is %s
                    '''
                    % (HolidayName, TheDate)
                )
        for i in Holidays2021bank:
            if HolidayName == i.name and HolidayDate == i.date:
                TempAddedHolidays.add(i)
                print('''
Success: 
{}, has been added to the holiday list.
                '''.format(i))
        print('=============')
        while True:
            selection = str(input('Would you like to continue adding holidays? [y/n]: ')).strip().lower()
            if selection =='y' or selection == 'n':
                break
            else:
                print("Please input either 'y' or 'n'.")
        if selection == 'y':
            add_a_holiday()
        else:
            print('Returning to main.')
            main_menu()

def delete_message(decorated_fn):
    def inner_fn(*args, **kwargs):
        removed_obj = decorated_fn(*args, **kwargs)
        print('''
Success:
{}, has been removed from the holiday list.
        '''.format(removed_obj))
    return inner_fn

@delete_message
def remove_an_obj(set, obj):
    for i in set:
        if obj == i.name:
            holiday_to_remove = i
    set.discard(holiday_to_remove)
    return holiday_to_remove

def remove_a_holiday():
    print('''
Remove a holiday
================
    ''')
    if len(TempAddedHolidays) != 0:
        while True:
            HolidayName = str(input("Please input the holiday name (alternatively you may hit 'q' to cancel and "
                                    "return to main):"))
            HolidayNames = [i.name for i in TempAddedHolidays]
            if HolidayName == 'q':
                break
            elif HolidayName not in HolidayNames:
                print("Either you've inputted the name incorrectly or this holiday is not in the list of added "
                      "holidays. Either way please try again.")
            else:
                break
        if HolidayName == 'q':
            print('Returning to main.')
            main_menu()
        else:
            remove_an_obj(TempAddedHolidays, HolidayName)
            while True:
                selection = str(input('Would you like to continue removing holidays? [y/n]:')).strip().lower()
                if selection == 'y' or selection == 'n':
                    break
                else:
                    print("Please input either 'y' or 'n'.")
            if selection == 'y':
                remove_a_holiday()
            else:
                print('Returning to main.')
                main_menu()
    else:
        print('There are no holidays to remove. Going back to the main menu.')
        main_menu()

def save_holiday_list():
    global AddedHolidays
    print('''
Saving Holiday List
===================
    ''')
    while True:
        selection = str(input("Are you sure you want to save your changes? [y/n]:"))
        if selection == 'y' or selection == 'n':
            break
        else:
            print("Please input either 'y' or 'n'.")
    if selection == 'n':
        print('''
Canceled:
Holiday list file save canceled.
        ''')
        main_menu()
    else:
        AddedHolidays = list(TempAddedHolidays)
        print('''
Success:
Your changes have been saved.
        ''')
        main_menu()

def get_dates_by_week_year(num, year):
    startdate = time.asctime(time.strptime('{} {} 0'.format(year,num), '%Y %W %w'))
    startdate = datetime.datetime.strptime(startdate, '%a %b %d %H:%M:%S %Y').date()
    dates = [startdate]
    for i in range(1, 7):
        dates.append(startdate + datetime.timedelta(days=i))
    return dates

def view_holiday():
    print('''
View Holidays
==============
    ''')
    while True:
        try:
            year = int(input('Which year? [input in yyyy format]:'))
            week = int(input('Which a week (in 1-52 format)? [enter 0 for current week]:'))
            break
        except:
            print("Good work following instructions! Now why don't we give that another go.")
    if week == 0:
        weeknum = datetime.datetime.now().isocalendar()[1]
        current_week = get_dates_by_week_year(weeknum, 2021)
        while True:
            selection = str(input("Would you like to see this week's weather? [y/n]:")).lower().strip()
            if selection == 'y' or selection == 'n':
                break
            else:
                print("Good work following instructions! Now why don't we give that another go.")
                continue
        if selection == 'y':
            print('These are the holidays for this week:')
            d1 = list(filter(lambda x: x.date in current_week, Holidays2021bank))
            # print(*d1, sep='\n')
            for i in d1:
                for k,v in CurrentWeatherDict.items():
                    if str(i.date) == k:
                        print(i,'- '+v)
            choice = str(input("Hit 'q' to return to main or any other letter to re-search:"))
            if choice == 'q':
                main_menu()
            else:
                view_holiday()
        else:
            print('These are the holidays for this week:')
            d2 = list(filter(lambda x: x.date in current_week, Holidays2021bank))
            print(*d2, sep='\n')
            choice = str(input("Hit 'q' to return to main or any other letter to re-search:"))
            if choice == 'q':
                main_menu()
            else:
                view_holiday()
    else:
        date_list = get_dates_by_week_year(week, year)
        print('These are the holidays for this week:')
        d = list(filter(lambda x: x.date in date_list, Holidays2021bank))
        print(*d, sep='\n')
        choice = str(input("Hit 'q' to return to main or any other letter to re-search:"))
        if choice == 'q':
            main_menu()
        else:
            view_holiday()




def main():
    start_menu()
    print(*AddedHolidays, sep='\n')

main()












'''
Notes: This section simply contains notes for when I was testing things in my code. You may read this section if you'd
like but it's not really relevant to any grading.

# holiday1 = Holidays2021bank[0].name
# 
# for i in Holidays2021bank:
#     if holiday1 == i.name:
#         print(i)
#         print(i.date)



'''


