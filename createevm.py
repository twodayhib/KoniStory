from web3 import Web3

def create_eth_wallets(num_wallets):
    w3 = Web3()
    wallets = []

    for _ in range(num_wallets):
        acc = w3.eth.account.create()
        private_key = w3.to_hex(acc._private_key)
        address = acc.address
        wallet = {
            'address': address,
            'private_key': private_key,
        }
        wallets.append(wallet)

    return wallets

def save_addresses_to_txt(wallets, address_filename='address.txt'):
    with open(address_filename, mode='w') as file:
        for wallet in wallets:
            file.write(f"{wallet['address']}\n")

def save_wallet_data_to_txt(wallets, walletdata_filename='walletdata.txt'):
    with open(walletdata_filename, mode='w') as file:
        for wallet in wallets:
            file.write(f"Address: {wallet['address']}, Private Key: {wallet['private_key']}\n")

if __name__ == "__main__":
    num_wallets = int(input("Enter the number of wallets to create: "))
    wallets = create_eth_wallets(num_wallets)

    save_addresses_to_txt(wallets)
    save_wallet_data_to_txt(wallets)

    print(f"{num_wallets} wallets saved to address.txt and walletdata.txt.")
