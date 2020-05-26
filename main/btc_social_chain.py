from __future__ import print_function
import argparse
import json
import urllib.request
import datetime
import sys
import random

__authors__ = ["N Miller"]
__date__ = 20200524
__description__ = "Bitcoin Social Chaining"


if sys.version_info[0] == 3:
    get_input = input
elif sys.version_info[0] == 2:
    get_input = raw_input

# Unix Timestamp Converter
def unix_converter(timestamp):
    date_ts = datetime.datetime.fromtimestamp(timestamp)
    return date_ts.strftime('%m/%d/%Y %I:%M:%S %p')


#How many hops??
#Check first degree, second degree, etc.
#Timeout for really large ones :: possible exchanges / tumblers


#Add in another parameter for layers / depth of search
def main(address):
        starting_account = get_address_json(address)
        prompt_address_main(starting_account)

#Create JSON account object and print the header for a given bitcoin address,
#Returns the JSON account
def get_address_json(address):
    account_raw = get_address(address)
    starting_account = json.loads(account_raw.read())
    print_header(starting_account)
    return starting_account

#Prints the prompt options for an account JSON Object
def prompt_address_main(starting_account):
    transactions_struct_created = False
    direct_contacts_struct_created = False
    while(True):
        next_action = input("What Next? ('help' to list all commands) :: \n")
        if (next_action == "txs" or next_action == "t"):
            print("\n")
            print_transactions(starting_account)
            if not(direct_contacts_struct_created):
                direct_contacts = create_direct_contact_struct(starting_account)
                direct_contacts_struct_created = True
            print("\n")
        elif (next_action == "contacts" or next_action == "c"):
            if not(direct_contacts_struct_created):
                direct_contacts = create_direct_contact_struct(starting_account)
                direct_contacts_struct_created = True
            print("\n")
            print_direct_contact_list(direct_contacts)
            print("\n")
        elif (next_action == "exit" or next_action == "e"):
            print("Goodbye")
            sys.exit(1)
        elif next_action == "help" or next_action == "h":
            print("\n")
            print_main_options()
            print("\n")
        elif next_action == "addr" or next_action == "a":
            print("\n")
            new_address = input("Enter the new address :: ")
            main(new_address)
            print("\n")
        else:
            print("unknown command, try again")

#Retrieve JSON Object of Bitcoin address from blockchain.info API
def get_address(address):
    url = 'https://blockchain.info/address/{}?format=json'
    formatted_url = url.format(address)
    try:
        return urllib.request.urlopen(formatted_url)
    except urllib.error.URLError:
        print("URL Error Received for {}".format(formatted_url))
        sys.exit(1)


#Print general account information for a bitcoin address, takes in a dict
def print_header(account):
    print('{:=^25}'.format(''))
    print('Starting Bitcoin Account')
    prRed(account['address'])
    print('Current Balance: {:.8f} BTC'.format(
        account['final_balance'] * 10**-8 ))
    print('Total Sent: {:.8f} BTC'.format(
        account['total_sent'] * 10**-8 ))
    print('Total Recieved: {:.8f} BTC'.format(
        account['total_received'] * 10**-8 ))
    print('Number of Transactions:', account['n_tx'])
    print('{:=^25}'.format(''))
    print("\n")

#Returns an array with all bitcoin addresses for transaction get_inputs
#Takes in a transaction dictionary


#Convert BTC To USD and Print!!


def get_input_addresses(tx):
    inputs = []
    for input_addr in tx['inputs']:
        if 'addr' in input_addr['prev_out']:
            inputs.append(input_addr['prev_out']['addr'])
        else:
            inputs.append("**No associated address**")
    return inputs
    print('{:=^25}'.format(''))
    print("\n")

#Prints all of the transactions associated with a BTC JSON object

def create_transactions_struct(account):
    transactions = {}
    for i, tx in enumerate(account['txs']):
        transactions[tx['hash']] = {}
        transactions[tx['hash']]['date'] = tx['time']
        transactions[tx['hash']]['inputs'] = get_input_addresses(tx)
        transactions[tx['hash']]['outputs'] = tx['out']

        #tx out will have multiple output transactions all from the same input source
        #Ignore any where the input is not the user??
        #Which transactions do we actually care about?
        sum = 0
        output_addrs = []
        for outputs in tx['out']:
            sum += outputs['value']
            if 'addr' in outputs:
                output_addrs.append(outputs['addr'])
            else: output_addrs.append("**Unknown Address**")
        transactions[tx['hash']]['output_addrs'] = output_addrs

        dir = False
        if account['address'] in transactions[tx['hash']]['inputs']:
            dir = True
        # True for out, False for in to the source address
        transactions[tx['hash']]['dir'] = dir
        transactions[tx['hash']]['total_value'] = sum
        transactions[tx['hash']]['num'] = i
    return transactions


#Create a contact dictionary :: Use their address as a key
# Multiple fields of interest!
# Each contact has the following fields
# txs :: list of all associated transactions
# in_txs :: list of all receipt transactions
# out_txs :: List of all sent transactions
# total_in :: total recieved from target
# total_out :: total sent to target
# color :: randomly generated color value
def create_direct_contact_struct(account):
    direct_contacts = {}
    for tx in account['txs']:
        for outputs in tx['out']:
            inputs = get_input_addresses(tx)
            # If target address is the recipient
            if ('addr' in outputs and outputs['addr'] == account['address']):
                for input in inputs:
                    # if not first time adding to this contact
                    if input in direct_contacts:
                        direct_contacts[input]['txs'].append(tx['hash'])
                        direct_contacts[input]['out_txs'].append(tx['hash'])
                        direct_contacts[input]['total_out'] += outputs['value']
                    #If this is the first time initializing the contact
                    else:
                        direct_contacts[input] = {}
                        direct_contacts[input]['txs'] = []
                        direct_contacts[input]['txs'].append(tx['hash'])
                        direct_contacts[input]['out_txs'] = []
                        direct_contacts[input]['out_txs'].append(tx['hash'])
                        direct_contacts[input]['in_txs'] = []
                        direct_contacts[input]['total_out'] = outputs['value']
                        direct_contacts[input]['total_in'] = 0
                        direct_contacts[input]['color'] = "%03x" % random.randint(0, 0xFFF)
            #If target address is the sender
            elif account['address'] in inputs:
                if 'addr' in outputs:
                    if outputs['addr'] in direct_contacts:
                        direct_contacts[outputs['addr']]['txs'].append(tx['hash'])
                        direct_contacts[outputs['addr']]['in_txs'].append(tx['hash'])
                        direct_contacts[outputs['addr']]['total_in'] += outputs['value']

                    else:
                        direct_contacts[outputs['addr']] = {}
                        direct_contacts[outputs['addr']]['txs'] = []
                        direct_contacts[outputs['addr']]['txs'].append(tx['hash'])
                        direct_contacts[outputs['addr']]['in_txs'] = []
                        direct_contacts[outputs['addr']]['in_txs'].append(tx['hash'])
                        direct_contacts[outputs['addr']]['out_txs'] = []
                        direct_contacts[outputs['addr']]['total_in'] = outputs['value']
                        direct_contacts[outputs['addr']]['total_out'] = 0
                        direct_contacts[outputs['addr']]['color'] = "%03x" % random.randint(0, 0xFFF)

                # Special Case when sending address is not known
                # For now, just create a special output value for this!
                else:
                    if "no_rec_addr" in outputs:
                        direct_contacts["no_rec_addr"]['txs'].append(tx['hash'])
                        direct_contacts["no_rec_addr"]['in_txs'].append(tx['hash'])
                        direct_contacts["no_rec_addr"]['total_in'] += outputs['value']
                    else:
                        direct_contacts["no_rec_addr"]['txs'] = [tx['hash']]
                        direct_contacts["no_rec_addr"]['in_txs'] = [tx['hash']]
                        direct_contacts["no_rec_addr"]['out_txs'] = []
                        direct_contacts["no_rec_addr"]['total_in'] = outputs['value']
                        direct_contacts["no_rec_addr"]['total_out'] = 0
                        direct_contacts["no_rec_addr"]['color'] = "%03x" % random.randint(0, 0xFFF)
    return direct_contacts

def print_direct_contact_list(direct_contacts):
    print('{:=^25}'.format(''))
    prCyan("Direct Contact List")
    for contact_addr in direct_contacts:
        print('{:=^25}'.format(''))
        prLightPurple(contact_addr)
        prGreen("Total Sent to Target :: {}".format(direct_contacts[contact_addr]['total_out']))
        print("\tAssociated transaction hashes ::")
        for hash_val in direct_contacts[contact_addr]['out_txs']:
            print("\t\t{}".format(hash_val))
        prYellow("Total Recieved from Target :: {}".format(direct_contacts[contact_addr]['total_in']))
        print("\tAssociated transaction hashes ::")
        for hash_val in direct_contacts[contact_addr]['in_txs']:
            print("\t\t{}".format(hash_val))
        print('{:=^25}'.format(''))

def print_transactions(account):
    print('{:=^25}'.format(''))
    prCyan('Account Transactions for')
    prRed('{}'.format(account['address']))
    for i, tx in enumerate(account['txs']):
        print('{:=^25}'.format(''))
        print('Transaction #{}'.format(i))
        print('Transaction Hash: ', tx['hash'])
        print('Transaction Date: {}'.format(unix_converter(tx['time'])))
        for outputs in tx['out']:
            inputs = get_input_addresses(tx)
            #Multiple by 10^-8 to convert to actual BTC value
            if ('addr' in outputs and outputs['addr'] == account['address']) or account['address'] in inputs:
                if len(inputs) > 1:
                    if 'addr' in outputs:
                        prRed('{} --> {} ({:.8f} BTC)'.format(
                            ' & '.join(inputs), outputs['addr'],
                            outputs['value'] * 10**-8))
                    else:
                        prRed('{} --> {} ({:.8f} BTC)'.format(
                            ' & '.join(inputs), "**No associated address**", outputs['value'] * 10**-8))
                else:
                    if 'addr' in outputs:
                        prRed('{} --> {} ({:.8f} BTC)'.format(
                            ''.join(inputs), outputs['addr'],
                            outputs['value'] * 10**-8))
                    else:
                        prRed('{} --> {} ({:.8f} BTC)'.format(
                            ''.join(inputs), "**No associated address**", outputs['value'] * 10**-8))
            else:
                if len(inputs) > 1:
                    if 'addr' in outputs:
                        print('{} --> {} ({:.8f} BTC)'.format(
                            ' & '.join(inputs), outputs['addr'],
                            outputs['value'] * 10**-8))
                    else:
                        print('{} --> {} ({:.8f} BTC)'.format(
                            ' & '.join(inputs), "**No associated address**", outputs['value'] * 10**-8))
                else:
                    if 'addr' in outputs:
                        print('{} --> {} ({:.8f} BTC)'.format(
                            ''.join(inputs), outputs['addr'],
                            outputs['value'] * 10**-8))
                    else:
                        print('{} --> {} ({:.8f} BTC)'.format(
                            ''.join(inputs), "**No associated address**", outputs['value'] * 10**-8))
        print('{:=^25}'.format(''))

#General command information
def print_main_options():
    print('{:=^25}'.format(''))
    print(" 'contacts' / 'c' -> List all direct contacts ")
    print(" 'txs' / 't' -> List all transactions")
    print(" 'addr' / 'a' -> Search an address")
    print(" 'deep' / 'd' -> Deep Web Search")
    print(" 'surface' / 's' -> Surface Web Search")
    print(" 'voila' / 'v' -> Show me everything")
    print(" 'exit' / 'e' -> See you next time")
    print(" 'help' / 'h' -> List all commands")
    print('{:=^25}'.format(''))


#Colored Printing
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))
def prLightPurple(skk): print("\033[94m {}\033[00m" .format(skk))
def prPurple(skk): print("\033[95m {}\033[00m" .format(skk))
def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prLightGray(skk): print("\033[97m {}\033[00m" .format(skk))
def prBlack(skk): print("\033[98m {}\033[00m" .format(skk))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Built by {}. Version {}'.format(
            ", ".join(__authors__), __date__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('ADDR', help="Starting Bitcoin Address")
    args = parser.parse_args()
    print('{:=^25}'.format(''))
    print('{}'.format('Bitcoin Contact Chaining'))
    print('{:=^25}'.format(''))
    print("\n")
    main(args.ADDR)
