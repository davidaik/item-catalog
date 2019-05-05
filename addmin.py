#!/system/bin/env python3
import re

import db_api


# Like { 1: 'myemail@gmail.com'}, for letting the user
# select email using number input from console
admins_index = {}


# For checking if email already exists.
admins_list = []


def isValidGmail(email):
    if re.search('.*@gmail.com$', email):
        return True
    else:
        return False


def prepareAdminsIndex(admins):
    global admins_index
    global admins_list

    admins_list.clear()

    i = 1
    for admin in admins:
        admins_list.append(admin.email)
        admins_index[i] = admin.email
        i += 1


def printAdmins(admins):
    i = 1
    for admin in admins:
        print('[{}] {}'.format(i, admin.email))
        i += 1


def promptAndAddNewAdmin():
    email = input("Enter new admin Gmail address: ")
    if not isValidGmail(email):
        print('Invalid Gmail address. Try again.')
        promptAndAddNewAdmin()
        return
    if email in admins_list:
        print('Admin {} already exists!'.format(email))
    else:
        db_api.add_admin(email)
        print('Admin added!')


def promptRemoveOrAddAdmin():
    printAdmins(admins)
    user_input = input(
        'Enter an admin number to remove it, or enter \'n\' to add a new admin: ')
    if user_input == 'n':
        promptAndAddNewAdmin()
    else:
        try:
            user_input = int(user_input)
            if user_input in admins_index:
                db_api.remove_admin(admins_index[user_input])
                print('Admin {} removed!'.format(admins_index[user_input]))
            else:
                print('Incorrect input. Try again.')
                promptRemoveOrAddAdmin()
        except ValueError:
            print('Incorrect input. Try again.')
            promptRemoveOrAddAdmin()


if __name__ == '__main__':
    admins = db_api.get_admins()
    prepareAdminsIndex(admins)

    try:
        if len(admins) == 0:
            # First time setup. Add new admin.
            print('There are currently no admins.')
            promptAndAddNewAdmin()
        else:
            promptRemoveOrAddAdmin()
    except KeyboardInterrupt:
        print('\nCancelled by user. Exiting...')
