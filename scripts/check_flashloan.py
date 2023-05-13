from brownie import interface, config, network, TestFlashLoan
from scripts.helper_scripts import get_account


def get_weth(_account, _amount=1):
    # ABI
    # Address
    print(f"Account {_account.address} ETH balance: {_account.balance()}")
    weth = interface.IwETH(config["networks"][network.show_active()]["weth_token"])

    print(f"Current wallet wETH balance: {weth.balanceOf(_account.address)}")
    print("Depositing 1 ETH for wETH...")
    tx = weth.deposit({"from": _account, "value": _amount * (10**18)})
    tx.wait(1)
    print("1 ETH deposited for wETH.")

    print(f"Current wallet wETH balance: {weth.balanceOf(_account.address)}")
    print("....\n\n")
    return tx


def recover_weth(_account, _from, _amount=1):
    weth = interface.IwETH(config["networks"][network.show_active()]["weth_token"])
    tx = _from.recoverERC20(
        _amount * (10**18),
        weth.address,
        {"from": _account},
    )
    tx.wait(1)

    print(f"Contract now has {weth.balanceOf(_from.address)} wETH")
    print(f"And wallet has {weth.balanceOf(_account.address)} wETH")
    print("....\n\n")


def transfer_weth_to(_account, _to, _amount=1):
    weth = interface.IwETH(config["networks"][network.show_active()]["weth_token"])
    tx = weth.transfer(_to, _amount * (10**18), {"from": _account})
    tx.wait(1)
    print(f"Wallet balance: {weth.balanceOf(_account.address)}")
    print(f"Balance of contract {_to}: {weth.balanceOf(_to)}")
    print("....\n\n")


def deploy_flashloan(_account):
    print(f"Deploying the FlashTemplate contract to {network.show_active()}")
    contract = TestFlashLoan.deploy(
        config["networks"][network.show_active()]["weth_token"],
        {"from": _account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Contract deployed successfully to {contract.address}")
    print("....\n\n")
    return contract


def main() -> None:
    print(f"Connected: {network.is_connected()}")
    account = get_account()

    flash_contract = deploy_flashloan(account)

    print("Getting wETH....")
    get_weth(account)

    print(f"Transferring wETH to contract {flash_contract.address}")
    transfer_weth_to(account, flash_contract.address)

    print(f"Initiating flash loan test...")
    # solid lizard exchange, that I picked below, has a high fee.  .004 fee multiplier didn't work so I bumped to .005
    tx = flash_contract.initiateWethFlashloan(
        "0xc2573d86eCA05173300cF68D5519F444a76dFeB9",
        True,
        (2 * (10**18)),
        ((2 + (2 * 0.005)) * (10**18) + 1),
    )
    tx.wait(1)

    print(f"Maximum WETH held: {flash_contract.maxTest()}")
    print(f"Was token0: {flash_contract.testToken0()}")
    print("....\n\n")

    # print("Getting the wETH back...")
    # recover_weth(account, flash_contract)


if __name__ == "__main__":
    main()
