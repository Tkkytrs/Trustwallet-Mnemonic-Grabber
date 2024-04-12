import os

x = int(input("Choose Where To Go, 1 - eth , 2- btc"))
os.system("cls || clear")
if x == 1:
    os.system("python3 eth.py")
else:
    os.system("python3 btc.py")