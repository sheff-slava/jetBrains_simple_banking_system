import random
import sqlite3


def luhn_algorithm(card, control_number=False):
    numbers = list(card)
    sum_ = 0
    for index in range(len(numbers) // 2 + len(numbers) % 2):
        sum_ += (int(numbers[2 * index]) * 2) // 10 + (int(numbers[2 * index]) * 2) % 10
        if index != len(numbers) // 2:
            sum_ += int(numbers[2 * index + 1])
    if control_number:
        return sum_

    return True if sum_ % 10 == 0 else False


conn = sqlite3.connect('card.s3db')
cursor = conn.cursor()
try:
    cursor.execute('CREATE TABLE card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
except sqlite3.OperationalError:
    pass
random.seed()
print('''1. Create an account
2. Log into account
0. Exit''')
action = int(input())
while action != 0:
    if action == 1:
        card_number = '400000'
        for _ in range(9):
            card_number += str(random.randint(0, 9))
        card_number += str((10 - luhn_algorithm(card_number, True) % 10) % 10)
        pin = ''
        for _ in range(4):
            pin += str(random.randint(0, 9))

        print('\nYour card has been created', 'Your card number:', card_number,
              'Your card PIN:', pin, sep='\n', end='\n')
        pin = '"' + pin + '"'
        card_number = '"' + card_number + '"'
        cursor.execute('SELECT id FROM card')
        id_ = len(cursor.fetchall())
        cursor.execute(f'INSERT INTO card VALUES ({id_}, {card_number}, {pin}, 0);')
        conn.commit()
    elif action == 2:
        card_number = input('\nEnter your card number:\n')
        pin = input('Enter your PIN:\n')
        cursor.execute('SELECT number FROM card')
        cards = cursor.fetchall()
        cards = [card[0] for card in cards]
        if card_number not in cards:
            print('\nWrong card number or PIN!')
        else:
            cursor.execute(f'SELECT pin FROM card WHERE number = {card_number}')
            card_pin = cursor.fetchone()[0]
            if card_pin != pin:
                print('\nWrong card number or PIN!')
            else:
                print('\nYou have successfully logged in!\n')
                print('1. Balance', '2. Add income', '3. Do transfer',
                      '4. Close account', '5. Log out', '0. Exit', sep='\n')
                action_int = int(input())
                while action_int != 0:
                    if action_int == 1:
                        cursor.execute(f'SELECT balance FROM card WHERE number = {card_number}')
                        balance = cursor.fetchone()[0]
                        print('\nBalance:', balance, end='\n')
                    elif action_int == 2:
                        income = int(input('\nEnter income:\n'))
                        cursor.execute(f'SELECT balance FROM card WHERE number = {card_number}')
                        balance = cursor.fetchone()[0]
                        cursor.execute(f'UPDATE card SET balance = {balance + income} WHERE number = {card_number}')
                        conn.commit()
                        print('Income was added!')
                    elif action_int == 3:
                        print('\nTransfer')
                        destination_card = input('Enter card number:\n')
                        if destination_card == card_number:
                            print("You can't transfer money to the same account!\n")
                        elif not luhn_algorithm(destination_card):
                            print('Probably you made a mistake in the card number. Please try again!')
                        elif destination_card not in cards:
                            print('Such a card does not exist.')
                        else:
                            transfer = int(input('Enter how much money you want to transfer:\n'))
                            cursor.execute(f'SELECT balance FROM card WHERE number = {card_number}')
                            available_money = cursor.fetchone()[0]
                            if transfer > available_money:
                                print('Not enough money!\n')
                            else:
                                cursor.execute(
                                    f'UPDATE card SET balance = {transfer} WHERE number = {destination_card}')
                                cursor.execute(
                                    f'UPDATE card SET balance = {available_money - transfer} WHERE number = {card_number}')
                                conn.commit()
                                print('Success!\n')
                    elif action_int == 4:
                        cursor.execute(f'DELETE FROM card WHERE number = {card_number}')
                        conn.commit()
                        print('\nThe account has been closed!')
                        break
                    elif action_int == 5:
                        print('\nYou have successfully logged out!')
                        break
                    print('\n1. Balance', '2. Add income', '3. Do transfer',
                          '4. Close account', '5. Log out', '0. Exit', sep='\n')
                    action_int = int(input())
                else:
                    break
    print('\n1. Create an account', '2. Log into account', '0. Exit', sep='\n')
    action = int(input())
print('\nBye!')
