""" Basic Bitcoin Address Lookup """
from __future__ import print_function
import argparse
import json
import urllib.request
import datetime
import sys

__authors__ = ["N Miller"]
__date__ = 20200524
__description__ = "Bitcoin Address Lookup from blockchain.info API"

if sys.version_info[0] == 3:
    get_input = input
elif sys.version_info[0] == 2:
    get_input = raw_input

# Unix Timestamp Converter
def unix_converter(timestamp):
    date_ts = datetime.datetime.fromtimestamp(timestamp)
    return date_ts.strftime('%m/%d/%Y %I:%M:%S %p')


def main(address):
    account_raw = get_address(address)
    account = json.loads(account_raw.read())
    print_transactions(account)

#Generates JSON Object from Bitcoin Address with Blockchain.info API Request
def get_address(address):
    url = 'https://blockchain.info/address/{}?format=json'
    formatted_url = url.format(address)
    try:
        return urllib.request.urlopen(formatted_url)
    except urllib.error.URLError:
        print("URL Error Received for {}".format(formatted_url))
        sys.exit(1)


def print_transactions(account):
    print_header(account)
    print('*** Transactions ***')
    for i, tx in enumerate(account['txs']):
        print('Transaction #{}'.format(i))
        print('Transaction Hash: ', tx['hash'])
        print('Transaction Date: {}'.format(unix_converter(tx['time'])))
        for outputs in tx['out']:
            inputs = get_inputs(tx)
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
        print("\n")



def print_header(account):
    print('Address:', account['address'])
    print('Current Balanace: {:.8f} BTC'.format(
        account['final_balance'] * 10**-8 ))
    print('Total Sent: {:.8f} BTC'.format(
        account['total_sent'] * 10**-8 ))
    print('Total Recieved: {:.8f} BTC'.format(
        account['total_received'] * 10**-8 ))
    print('Number of Transactions:', account['n_tx'])
    print('{:=^25}'.format(''))
    print("\n")

def get_inputs(tx):
    inputs = []
    for input_addr in tx['inputs']:
        inputs.append(input_addr['prev_out']['addr'])
    return inputs
    print('{:=^25}'.format(''))
    print("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog='Built by {}. Version {}'.format(
            ", ".join(__authors__), __date__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('ADDR', help="Bitcoin Address")
    args = parser.parse_args()
    print('{:=^25}'.format(''))
    print('{}'.format('Bitcoin Address Lookup'))
    print('{:=^25}'.format(''))
    print("\n")

    main(args.ADDR)
