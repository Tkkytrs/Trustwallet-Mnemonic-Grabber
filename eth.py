import random
import hashlib
import aiohttp
import asyncio
from termcolor import colored
from eth_account import Account
from mnemonic import Mnemonic
from concurrent.futures import ThreadPoolExecutor
from pyfiglet import Figlet
import colorama
import random

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



async def generate_random_words():
    mnemo = Mnemonic("english")
    return mnemo.generate(128).split()

def generate_ethereum_address(words):
    phrase = ' '.join(words)
    private_key = hashlib.sha256(phrase.encode()).hexdigest()
    
    account = Account.from_key(private_key)
    eth_address = account.address
    return eth_address

async def check_balance_ethereum(session, address):
    url = f'https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey=K52TG42HNFNI1W8PQU7GN3HGMFGE57EMKD'
    async with session.get(url) as response:
        data = await response.json()

        if data['status'] == '1':
            balance_wei = int(data['result'])
            balance_eth = balance_wei / 10**18  # Convert Wei to Ether
            return balance_eth
        else:
            return "0"

async def process_address(session, live_counter_list, dead_counter_list, balanced_addresses):
    words = await generate_random_words()
    eth_address = generate_ethereum_address(words)
    balance = await check_balance_ethereum(session, eth_address)

    if balance is not None:
        if balance != "0":
            live_counter_list[0] += 1
            if balance > 0.000000:
                balanced_addresses.append(f'{eth_address} |{" ".join(words)} | BALANCE: {balance:.6f} ETH')
            print(colored(f'TOTAL LIVE: {live_counter_list[0]} | MNEMONIC: {" ".join(words)} | BALANCE: {balance:.6f} ETH | ADDRESS: {eth_address}', 'green'))
        else:
            dead_counter_list[0] += 1
            print(colored(f'TOTAL DEAD: {dead_counter_list[0]} | MNEMONIC: {" ".join(words)} | BALANCE: 0 [DEAD] | ADDRESS: {eth_address}', 'red'))

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
