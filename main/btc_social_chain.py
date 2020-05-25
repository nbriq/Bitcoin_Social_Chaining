from __future__ import print_function
import argparse
import json
import urllib.request
import datetime
import sys

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
    account_raw = get_address(address)
    starting_account = json.loads(account_raw.read())
    print_header(starting_account)

    while(True):
        next_action = input("What Next? ('help' to list all commands) :: \n")
        if (next_action == "txs" or next_action == "t"):
            print("\n")
            print_transactions(starting_account)
            txs = create_transactions_struct(starting_account)
            transactions_order_values(txs)
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
    print('Address:', account['address'])
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
        inputs.append(input_addr['prev_out']['addr'])
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
            output_addrs.append(outputs['addr'])
        transactions[tx['hash']]['output_addrs'] = output_addrs

        dir = False
        if account['address'] in transactions[tx['hash']]['inputs']:
            dir = True
        # True for out, False for in to the source address
        transactions[tx['hash']]['dir'] = dir
        transactions[tx['hash']]['total_value'] = sum
        transactions[tx['hash']]['num'] = i
    return transactions

def create_contact_struct(transactions):
    contacts = {}
    for tx in transactions:
        if transactions[tx]['dir']:

            print(transactions[tx]['inputs'])
            print(transactions[tx]['output_addrs'])
            print(transactions[tx]['total_value'])
    print("\n ************** \n")
    for tx in transactions:
        if not(transactions[tx]['dir']):
            print(transactions[tx]['inputs'])
            print(transactions[tx]['output_addrs'])
            print(transactions[tx]['total_value'])





def print_transactions(account):
    print('{:=^25}'.format(''))
    print('Account Transactions for')
    print('{}'.format(account['address']))
    for i, tx in enumerate(account['txs']):
        print('{:=^25}'.format(''))
        print('Transaction #{}'.format(i))
        print('Transaction Hash: ', tx['hash'])
        print('Transaction Date: {}'.format(unix_converter(tx['time'])))
        for outputs in tx['out']:
            inputs = get_input_addresses(tx)
            #Multiple by 10^-8 to convert to actual BTC value
            if len(inputs) > 1:
                print('{} --> {} ({:.8f} BTC)'.format(
                    ' & '.join(inputs), outputs['addr'],
                    outputs['value'] * 10**-8))
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
    print(" 'contacts' / 'c' -> List all contacts ")
    print(" 'txs' / 't' -> List all transactions")
    print(" 'addr' / 'a' -> Search an address")
    print(" 'deep' / 'd' -> Deep Web Search")
    print(" 'surface' / 's' -> Surface Web Search")
    print(" 'voila' / 'v' -> Show me everything")
    print(" 'exit' / 'e' -> See you next time")
    print(" 'help' / 'h' -> List all commands")
    print('{:=^25}'.format(''))

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
