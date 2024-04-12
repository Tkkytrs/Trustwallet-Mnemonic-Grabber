
import random
import hashlib
import aiohttp
import asyncio
from termcolor import colored
from bip32utils import BIP32Key
from mnemonic import Mnemonic
from concurrent.futures import ThreadPoolExecutor
from pyfiglet import Figlet
import colorama
import requests  # Import requests module

def lolcat(text):
    fig = Figlet()
    banner = fig.renderText(text)

    lines = banner.split('\n')
    colored_lines = []

    colorama.init(autoreset=True)

    color_list = [colorama.Fore.CYAN, colorama.Fore.BLUE, colorama.Fore.GREEN,
                  colorama.Fore.MAGENTA, colorama.Fore.YELLOW, colorama.Fore.RED]

    selected_colors = random.sample(color_list, 2)

    for line in lines:
        gradient_line = ""
        for i in range(len(line)):
            ratio = i / len(line)
            current_color = selected_colors[0] if ratio <= 0.5 else selected_colors[1]
            gradient_line += "{}{}".format(current_color, line[i])
        colored_lines.append(gradient_line)

    colored_banner = '\n'.join(colored_lines)
    print(colored_banner)

async def generate_mc():
    mnemo = Mnemonic("english")
    return mnemo.generate(256)

def generate_BTCereum_address(words):
    seed = hashlib.pbkdf2_hmac('sha512', words.encode('utf-8'), b'Bitcoin seed', 2048)
    master_key = BIP32Key.fromEntropy(seed)
    btc_address = master_key.Address()
    return btc_address

async def check_balance_BTCereum(session, address):
    url = f"https://blockchain.info/rawaddr/{address}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            if 'final_balance' in data:
                balance = data['final_balance'] / 100000000  # Convert from satoshis to BTC
                return balance
    return "0"


async def process_address(session, live_counter_list, dead_counter_list, balanced_addresses):
    words = await generate_mc()
    BTC_address = generate_BTCereum_address(words)
    balance = await check_balance_BTCereum(session, BTC_address)

    if balance is not None:
        if balance != "0":
            live_counter_list[0] += 1
            if balance > 0.000000:
                balanced_addresses.append(f'{BTC_address} |{words} | BALANCE: {balance:.6f} BTC')
            print(colored(f'TOTAL LIVE: {live_counter_list[0]} | MNEMONIC: {words} | BALANCE: {balance:.6f} BTC | ADDRESS: {BTC_address}', 'green'))
        else:
            dead_counter_list[0] += 1
            print(colored(f'TOTAL DEAD: {dead_counter_list[0]} | MNEMONIC: {words} | BALANCE: 0 [DEAD] | ADDRESS: {BTC_address}', 'red'))

async def main():
    num_threads = 5  # Adjust as needed
    live_counter_list = [0]  # Using a list to make it mutable
    dead_counter_list = [0]  # Using a list to make it mutable
    balanced_addresses = []

    async with aiohttp.ClientSession() as session:
        while True:
            tasks = [process_address(session, live_counter_list, dead_counter_list, balanced_addresses) for _ in range(num_threads)]
            await asyncio.gather(*tasks)

            # Check for balanced addresses and save them to a file
            if len(balanced_addresses) > 0:
                filename = f'data_{random.randint(1, 1000000)}.txt'
                with open(filename, 'w') as file:
                    file.write('\n'.join(balanced_addresses))
                print(colored(f'{len(balanced_addresses)} Balanced addresses saved to {filename}', 'yellow'))
                balanced_addresses = []  # Clear the list after saving

if __name__ == "__main__":
    lolcat("TKKYTRS")
    asyncio.run(main())
