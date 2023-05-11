from brownie import interface, config, network
from scripts.helper_scripts import get_account


def get_weth():
    # ABI
    # Address
    account = get_account()
    print(f"Account {account.address} balance: {account.balance()}")
    weth = interface.IwETH(config["networks"][network.show_active()]["weth_token"])
    weth_balance = weth.balanceOf(account.address)
    print(f"Current wETH balance: {weth_balance}")
    print("Depositing 1 ETH for wETH...")
    tx = weth.deposit({"from": account, "value": 1 * (10**18)})
    tx.wait(1)
    print("1 ETH deposited for WETH.")
    weth_balance = weth.balanceOf(account.address)
    print(f"Current wETH balance: {weth_balance}")
    return tx


def main() -> None:
    print(f"Currently running on the following network: {network.show_active()}")
    print(f"Connected: {network.is_connected()}")
    get_weth()


if __name__ == "__main__":
    main()
