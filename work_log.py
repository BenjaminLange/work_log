import csv
import re
import os
import sys

from datetime import datetime
from datetime import timedelta


WORK_LOG_FILENAME = 'work_log.csv'
TEMP_WORK_LOG_FILENAME = 'temp_work_log.csv'
FMT_MONTH_DAY_YEAR = '%m/%d/%y'
FMT_HOUR_MINUTE = '%H:%M'
FIELDNAMES = ['id', 'name', 'date', 'time_spent', 'notes']


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
    entry['name'] = input_name()
    print("How many minutes did you spend on {}?".format(entry['name']))
    print("You may specify a format after the time, seperated by a comma")
    entry['time_spent'] = input_time_spent()
    add_notes = input("Add notes? Y/n ").lower()
    if add_notes != 'n':
        entry['notes'] = input_notes()
    entry['date'] = datetime.now().strftime(FMT_MONTH_DAY_YEAR)
    with open(WORK_LOG_FILENAME, 'a', newline='') as work_log:
        work_log_writer = csv.DictWriter(work_log, fieldnames=FIELDNAMES)
        work_log_writer.writerow(entry)


def input_name():
    name = input("Task Name: ")
    return name


def input_time_spent(update=False):
    time_spent = input("Time Spent: ")
    if update:
        if time_spent == '':
            return ''
    if ',' in time_spent:
        entry_list = time_spent.split(',')
        entry_time = entry_list[0]
        entry_time_format = entry_list[1]
        return convert_string_to_timedelta(entry_time, entry_time_format)
    else:
        try:
            return convert_minutes_to_timedelta(time_spent)
        except ValueError:
            print("I don't recognize that format. Please try again.")
            return input_time_spent()


def input_notes():
    note_list = []
    notes = "A"
    print("Notes:")
    while notes != '':
        notes = input("> ")
        note_list.append(notes.replace('\\n', '\n'))
    notes = '\n'.join(note_list)
    return notes


def input_date(update=False):
    date = input("Date (MM/DD/YY): ")
    if update:
        if date == '':
            return ''
    try:
        date = datetime.strptime(date, FMT_MONTH_DAY_YEAR)
    except ValueError:
        print("I don't recognize that format, please try again.")
        return input_date()
    date = date.strftime(FMT_MONTH_DAY_YEAR)
    return date


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
    time_range = re.compile(r'\d{1,2}:\d{1,2} - \d{1,2}:\d{1,2}')
    time_format = re.compile(r'\d{1,2}:\d\d')
    minute_format = re.compile(r'^\d+$')
    if time_range.search(user_input):
        time_list = user_input.split('-')
        minimum = convert_string_to_timedelta(time_list[0].strip())
        maximum = convert_string_to_timedelta(time_list[1].strip())
        entries = []
        with open(WORK_LOG_FILENAME, 'r') as work_log:
            work_log_reader = csv.DictReader(work_log)
            for entry in work_log_reader:
                entry_time = convert_string_to_timedelta(
                    entry['time_spent'], '%H:%M:%S')
                if minimum <= entry_time <= maximum:
                    entries.append(entry)
        print_entries(entries)
    elif time_format.search(user_input):
        user_input = convert_string_to_timedelta(user_input)
    elif minute_format.search(user_input):
        user_input = convert_minutes_to_timedelta(user_input)
    else:
        error = "I don't recognize that format. Please try again.\n"
        return search_by_time_spent(error)
    with open(WORK_LOG_FILENAME, 'r') as work_log:
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
        start_date = datetime.strptime(
            date_list[0].strip(), FMT_MONTH_DAY_YEAR)
        end_date = datetime.strptime(
            date_list[1].strip(), FMT_MONTH_DAY_YEAR)
        entries = []
        with open(WORK_LOG_FILENAME, 'r') as work_log:
            work_log_reader = csv.DictReader(work_log)
            for entry in work_log_reader:
                entry_date = datetime.strptime(
                    entry['date'], FMT_MONTH_DAY_YEAR)
                if start_date <= entry_date <= end_date:
                    entries.append(entry)
        print_entries(entries)
    elif date.search(user_input):
        entries = []
        with open(WORK_LOG_FILENAME, 'r') as work_log:
            work_log_reader = csv.DictReader(work_log)
            for entry in work_log_reader:
                if user_input == entry['date']:
                    entries.append(entry)
        print_entries(entries)
    else:
        error = "I don't recognize that format. Please try again.\n"
        return search_by_date(error)
    input("\nPress enter to return to the main menu...")


def search_by_string():
    clear_screen()
    user_input = input("What would you like to search for? ").lower()
    entries = []
    with open(WORK_LOG_FILENAME, 'r') as work_log:
        work_log_reader = csv.DictReader(work_log)
        for entry in work_log_reader:
            if(user_input in entry['name'].lower() or
               user_input in entry['notes'].lower()):
                entries.append(entry)
    print_entries(entries)


def search_by_pattern():
    clear_screen()
    user_input = input("What pattern would you like to search for? ")
    search_pattern = re.compile(user_input)
    entries = []
    with open(WORK_LOG_FILENAME, 'r') as work_log:
        work_log_reader = csv.DictReader(work_log)
        for entry in work_log_reader:
            try:
                if (search_pattern.search(entry['name']) or
                        search_pattern.search(entry['notes'])):
                    entries.append(entry)
            except IndexError:
                pass
    print_entries(entries)


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
    if len(entries) == 0:
        print("\nNo results were found.\n")
        input("Press enter to return to the main menu...")
        start()
    counter = 0
    error = None
    while True:
        clear_screen()
        if len(entries) == 0:
            print("There are no more entries!")
            input("Press enter to return to the main menu...")
            start()
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
            edit_entry(entries[counter])
        else:
            counter += 1
            if counter > len(entries) - 1:
                counter -= 1
                error = "End of list. Can't move forward."


def delete_entry(entry_id):
    with open(WORK_LOG_FILENAME, 'r') as work_log:
        copy = open(TEMP_WORK_LOG_FILENAME, 'a', newline='')
        copy_writer = csv.DictWriter(copy, fieldnames=FIELDNAMES)
        copy_writer.writeheader()
        work_log_reader = csv.DictReader(work_log)
        for entry in work_log_reader:
            if entry['id'] == entry_id:
                continue
            else:
                copy_writer.writerow(entry)
        copy.close()
    os.remove(WORK_LOG_FILENAME)
    os.rename(TEMP_WORK_LOG_FILENAME, WORK_LOG_FILENAME)


def edit_entry(entry):
    print("\nUpdate each value or press enter to leave it unchanged.\n")
    prev_name = entry['name']
    prev_date = entry['date']
    prev_time_spent = entry['time_spent']
    prev_notes = entry['notes']
    new_name = input_name()
    entry['name'] = new_name or prev_name
    new_date = input_date(update=True)
    entry['date'] = new_date or prev_date
    new_time_spent = input_time_spent(update=True)
    entry['time_spent'] = new_time_spent or prev_time_spent
    new_notes = input_notes()
    entry['notes'] = new_notes or prev_notes

    with open(WORK_LOG_FILENAME, 'r') as work_log:
        copy = open(TEMP_WORK_LOG_FILENAME, 'a', newline='')
        copy_writer = csv.DictWriter(copy, fieldnames=FIELDNAMES)
        copy_writer.writeheader()
        work_log_reader = csv.DictReader(work_log)
        for prev_entry in work_log_reader:
            if prev_entry['id'] == entry['id']:
                copy_writer.writerow(entry)
            else:
                copy_writer.writerow(prev_entry)
        copy.close()
    os.remove(WORK_LOG_FILENAME)
    os.rename(TEMP_WORK_LOG_FILENAME, WORK_LOG_FILENAME)


def convert_string_to_timedelta(time, fmt=FMT_HOUR_MINUTE):
    time_range = datetime.strptime(time, fmt)
    time_range_delta = timedelta(hours=time_range.hour,
                                 minutes=time_range.minute,
                                 seconds=time_range.second)
    return time_range_delta


def convert_minutes_to_timedelta(minutes_string):
    minutes = int(minutes_string)
    if minutes >= 60:
        hours = int(minutes / 60)
        minutes = minutes % 60
        minutes_string = "{}:{}".format(hours, minutes)
        minutes_date_time = datetime.strptime(minutes, FMT_HOUR_MINUTE)
    else:
        minutes_date_time = datetime.strptime(minutes, '%M')
    minutes_delta = timedelta(hours=minutes_date_time.hour,
                              minutes=minutes_date_time.minute,
                              seconds=minutes_date_time.second)
    return minutes_delta


def get_next_id():
    with open(WORK_LOG_FILENAME, 'r') as work_log:
        work_log_reader = csv.DictReader(work_log)
        entry_id = 0
        for entry in work_log_reader:
            if int(entry['id']) > entry_id:
                entry_id = int(entry['id'])
        entry_id += 1
        return entry_id


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    start()
