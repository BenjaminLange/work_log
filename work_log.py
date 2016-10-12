import csv
import re
import os
import sys

from datetime import datetime
from datetime import timedelta


work_log_filename = "work_log.csv"


def start():
    while True:
        clear_screen()
        print("Select an option:")
        print("  e: Enter new entry (Default)")
        print("  s: Search")
        print("  q: Quit")
        user_input = input("> ").lower()
        if user_input == 'q':
            sys.exit()
        if user_input == 's':
            search()
        else:
            new_entry()


def new_entry():
    clear_screen()
    entry = {}
    entry['id'] = get_next_id()
    entry['name'] = input("Enter a name for the task: ")
    print("How many minutes did you spend on {}?".format(entry['name']))
    print("You may specify a format after the time, seperated by a comma")
    entry['time_spent'] = input("> ")
    if ',' in entry['time_spent']:
        entry_list = entry['time_spent'].split(',')
        entry_time = entry_list[0]
        entry_time_format = entry_list[1]
        entry['time_spent'] = convert_string_to_timedelta(entry_time, entry_time_format)
    else:
        entry['time_spent'] = convert_minutes_to_timedelta(entry['time_spent'])
    add_notes = input("Add notes? Y/n ").lower()
    note_list = []
    if add_notes != 'n':
        print("Enter any notes or comments. Enter a blank line to save.")
        notes = "A"
        while notes != '':
            notes = input("> ")
            note_list.append(notes.replace('\\n', '\n'))
    notes = '\n'.join(note_list)
    entry['notes'] = notes
    entry['date'] = datetime.now().strftime('%m/%d/%y')
    fieldnames = ['id', 'name', 'date', 'time_spent', 'notes']
    with open(work_log_filename, 'a', newline='') as work_log:
        work_log_writer = csv.DictWriter(work_log, fieldnames=fieldnames)
        work_log_writer.writerow(entry)


def search():
    clear_screen()
    print("What would you like to search by?")
    print("  d: Date (Default)")
    print("  t: Time spent")
    print("  e: Exact")
    print("  p: Pattern (Regex)")
    user_input = input("> ").lower()
    if user_input == 't':
        search_by_time_spent()
    elif user_input == 'e':
        search_by_string()
    elif user_input == 'p':
        search_by_pattern()
    else:
        search_by_date()


def search_by_time_spent(error=None):
    clear_screen()
    if error:
        print(error)
    print("Enter the minute amount to search for or search using %H:%M.")
    print("You may specify a time range using %H:%M - %H:%M")
    user_input = input("> ").strip()
    time_range = re.compile(r'\d{1,2}:\d\d - \d{1,2}:\d\d')
    time_format = re.compile(r'\d{1,2}:\d\d')
    minute_format = re.compile(r'^\d+$')
    if time_range.search(user_input):
        time_list = user_input.split('-')
        minimum = convert_string_to_timedelta(time_list[0].strip())
        maximum = convert_string_to_timedelta(time_list[1].strip())
        entries = []
        with open(work_log_filename, 'r') as work_log:
            work_log_reader = csv.DictReader(work_log)
            for entry in work_log_reader:
                entry_time = convert_string_to_timedelta(entry['time_spent'], '%H:%M:%S')
                if minimum <= entry_time <= maximum:
                    # print_entry(entry)
                    entries.append(entry)
        print_entries(entries)
    elif time_format.search(user_input):
        user_input = convert_string_to_timedelta(user_input)
    elif minute_format.search(user_input):
        user_input = convert_minutes_to_timedelta(user_input)
    else:
        error = "I don't recognize that format. Please try again.\n"
        return search_by_time_spent(error)
    with open(work_log_filename, 'r') as work_log:
        entries = []
        work_log_reader = csv.DictReader(work_log)
        for entry in work_log_reader:
            if entry['time_spent'] == str(user_input):
                entries.append(entry)
    print_entries(entries)


def search_by_date(error=None):
    clear_screen()
    if error:
        print(error)
    print("Please enter a date to search for (MM/DD/YY).")
    print("You may also search a date range using MM/DD/YY - MM/DD/YY")
    user_input = input("> ")
    date_range = re.compile(r'\d\d/\d\d/\d\d - \d\d/\d\d/\d\d')
    date = re.compile(r'\d\d/\d\d/\d\d')
    if date_range.search(user_input):
        date_list = user_input.split('-')
        start = datetime.strptime(date_list[0].strip(), '%m/%d/%y')
        end = datetime.strptime(date_list[1].strip(), '%m/%d/%y')
        with open(work_log_filename, 'r') as work_log:
            work_log_reader = csv.DictReader(work_log)
            logs = []
            for idx, entry in enumerate(work_log_reader):
                entry_date = datetime.strptime(entry['date'], '%m/%d/%y')
                if start <= entry_date <= end:
                    logs.append(entry)
            if len(logs) == 0:
                print("Sorry, no entries were found.")
            for log in logs:
                print_entry(log)
    elif date.search(user_input):
        with open(work_log_filename, 'r') as work_log:
            work_log_reader = csv.DictReader(work_log)
            logs = []
            for idx, entry in enumerate(work_log_reader):
                if user_input == entry['date']:
                    logs.append(entry)
            if len(logs) == 0:
                print("Sorry, no entries were found.")
            for log in logs:
                print_entry(log)
    else:
        error = "I don't recognize that format. Please try again.\n"
        return search_by_date(error)
    input("\nPress enter to return to the main menu...")


def search_by_string():
    clear_screen()
    user_input = input("What would you like to search for? ").lower()
    found = False
    with open(work_log_filename, 'r') as work_log:
        work_log_reader = csv.DictReader(work_log)
        for row in work_log_reader:
            if(user_input in row['name'].lower() or
               user_input in row['notes'].lower()):
                found = True
                print_entry(row)
    if not found:
        print("No results were found.")
    print()
    input("Press enter to return to the main menu...")


def search_by_pattern():
    clear_screen()
    user_input = input("What pattern would you like to search for? ")
    search = re.compile(user_input)
    found = False
    with open(work_log_filename, 'r') as work_log:
        work_log_reader = csv.DictReader(work_log)
        for row in work_log_reader:
            try:
                if search.search(row['name']) or search.search(row['notes']):
                    found = True
                    print_entry(row)
            except IndexError:
                pass
    if not found:
        print("No results were found.")
    print()
    input("Press enter to return to the main menu...")


def print_entry(entry):
    border = '-' * 50
    print(border)
    print(entry['name'])
    print("Date: {}".format(entry['date']))
    print("Time Spent: {}".format(entry['time_spent']))
    if entry['notes'] != '':
        print("Notes:\n{}\n{}".format('----------', entry['notes']))
    print(border)


def print_entries(entries):
    # Display records one at a time and allow edit/deletion and next/prev/exit
    counter = 0
    error = None
    while True:
        clear_screen()
        if error:
            print(error)
            input("Press enter to continue...")
            clear_screen()
            error = None
        print_entry(entries[counter])
        print("\nWhat would you like to do?")
        print("  n: Next entry (Default)")
        print("  p: Previous entry")
        print("  e: Edit entry")
        print("  d: Delete entry")
        print("  q: Quit to main menu")
        user_input = input("> ").lower()
        if user_input == 'q':
            start()
        elif user_input == 'p':
            if counter <= 0:
                error = "End of list. Can't go back."
                continue
            counter -= 1
        elif user_input == 'd':
            delete_entry(entries[counter]['id'])
            del entries[counter]
            if counter > len(entries) - 1:
                counter -= 1
        elif user_input == 'e':
            edit_entry(entries[counter]['id'])
        else:
            counter += 1
            if counter > len(entries) - 1:
                counter -= 1
                error = "End of list. Can't move forward."


def delete_entry(id):
    with open(work_log_filename, 'r') as work_log:
        fieldnames = ['id', 'name', 'date', 'time_spent', 'notes']
        copy = open('temp_work_log.csv', 'a', newline='')
        copy_writer = csv.DictWriter(copy, fieldnames=fieldnames)
        copy_writer.writeheader()
        work_log_reader = csv.DictReader(work_log)
        for entry in work_log_reader:
            if entry['id'] == id:
                continue
            else:
                copy_writer.writerow(entry)
        copy.close()
    os.remove(work_log_filename)
    os.rename("temp_work_log.csv", work_log_filename)


def edit_entry(id):
    pass


def convert_string_to_timedelta(time, fmt='%H:%M'):
    time_range = datetime.strptime(time, fmt)
    time_range = timedelta(hours=time_range.hour,
                           minutes=time_range.minute,
                           seconds=time_range.second)
    return time_range


def convert_minutes_to_timedelta(minutes):
    if int(minutes) > 60:
        minutes = int(minutes)
        hours = int(minutes / 60)
        minutes = minutes % 60
        minutes = "{}:{}".format(hours, minutes)
        minutes = datetime.strptime(minutes, '%H:%M')
    else:
        minutes = datetime.strptime(minutes, '%M')
    minutes = timedelta(hours=minutes.hour,
                        minutes=minutes.minute,
                        seconds=minutes.second)
    return minutes


def get_next_id():
    with open(work_log_filename, 'r') as work_log:
        work_log_reader = csv.DictReader(work_log)
        id = 0
        for entry in work_log_reader:
            if int(entry['id']) > id:
                id = int(entry['id'])
        id += 1
        return id


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    start()