from brownie import interface, config, network
from scripts.helper_scripts import get_account


def get_weth():
    # ABI
    # Address
    account = get_account()
    weth = interface.IwETH(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * (10**18)})
    tx.wait(1)
    print("ETH deposited for WETH.")
    return tx


def main() -> None:
    print(f"Currently running on the following network: {network.show_active()}")
    print(f"Connected: {network.is_connected()}")
    # get_weth()


if __name__ == "__main__":
    main()
