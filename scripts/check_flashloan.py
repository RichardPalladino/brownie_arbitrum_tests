from brownie import interface, config, network, TestFlashLoan
from scripts.helper_scripts import get_account


def get_weth(_account, _amount=1):
    # ABI
    # Address
    print(f"Account {_account.address} ETH balance: {_account.balance()}")
    weth = interface.IwETH(config["networks"][network.show_active()]["weth_token"])

    print(f"Current wallet wETH balance: {weth.balanceOf(_account.address)}")
    print(f"Depositing {_amount} ETH for wETH...")
    tx = weth.deposit({"from": _account, "value": _amount * (10**18)})
    tx.wait(1)
    print(f"{_amount} ETH deposited for wETH.")

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
    get_weth(account, 5)

    print(f"Transferring wETH to contract {flash_contract.address}")
    transfer_weth_to(account, flash_contract.address, 5)

    ### LizardSwap
    print(f"Initiating flash loan test with LizardSwap...")
    # solid lizard exchange, that I picked below, has a high fee.  .004 fee multiplier didn't work so I bumped to .005
    tx = flash_contract.initiateWethFlashloan(
        "0xc2573d86eCA05173300cF68D5519F444a76dFeB9",
        True,
        (2 * (10**18)),
        ((2 + (2 * 0.0041)) * (10**18)),
    )
    tx.wait(1)

    print(f"Maximum WETH held: {flash_contract.maxTest()}")
    print(f"Was token0: {flash_contract.testToken0()}")
    print("....\n\n")

    ### AlienFi
    print(f"Initiating flash loan test with AlienFi...")
    # .0025 fee
    tx = flash_contract.initiateWethFlashloan(
        "0x2408bcB8Edb820DAd4660dF627337c083EBA762a",
        False,
        (13 * (10**18)),
        ((13 + (13 * 0.0027)) * (10**18)),
    )
    tx.wait(1)

    print(f"Maximum WETH held: {flash_contract.maxTest()}")
    print(f"Was token0: {flash_contract.testToken0()}")
    print("....\n\n")

    ###  OREO SWAP
    print(f"Initiating flash loan test with OreoSwap...")
    # .0025 and .0026 fee didn't work.  Upped to .0027 A total of .0002 fee extra
    tx = flash_contract.initiateWethFlashloan(
        "0xBa06c51c44E087131249665e31719645641e5268",
        True,
        (2 * (10**18)),
        ((2 + (2 * 0.0032)) * (10**18)),
    )
    tx.wait(1)

    print(f"Maximum WETH held: {flash_contract.maxTest()}")
    print(f"Was token0: {flash_contract.testToken0()}")
    print("....\n\n")

    ###  SUSHI SWAP
    print(f"Initiating flash loan test with SushiSwap...")
    # Works with .0002 fee extra, for a total of .0032 fee, on the first try
    tx = flash_contract.initiateWethFlashloan(
        "0x905dfCD5649217c42684f23958568e533C711Aa3",
        True,
        (100 * (10**18)),
        ((100 + (100 * 0.0032)) * (10**18)),
    )
    tx.wait(1)

    ###  Camelot DEX
    print(f"Initiating flash loan test with Camelot...")
    # Going with .0032 - with a .0002 fee extra
    tx = flash_contract.initiateWethFlashloan(
        "0x84652bb2539513BAf36e225c930Fdd8eaa63CE27",
        True,
        (111 * (10**18)),
        ((111 + (111 * 0.0032)) * (10**18)),
    )
    tx.wait(1)

    ###  Arbitrum Exchange
    print(f"Initiating flash loan test with Arbitrum Exchange...")
    # Going with .0027 - with a .0002 fee extra - even though my config data says the average fee is .003
    tx = flash_contract.initiateWethFlashloan(
        "0x4C42fA9Ecc3A17229EDf0fd6A8eec3F11D7E00D3",
        True,
        (101 * (10**18)),
        ((101 + (101 * 0.0027)) * (10**18)),
    )
    tx.wait(1)

    ###  Ramses Exchange (uses proxies)
    print(f"Initiating flash loan test with Ramses...")
    # Going with .006 - with a .0002 fee extra - even though config says .002 fee and "stablefee" value is .0001
    tx = flash_contract.initiateWethFlashloan(
        "0x5513a48F3692Df1d9C793eeaB1349146B2140386",
        True,
        (131 * (10**18)),
        ((131 + (131 * 0.006)) * (10**18)),
    )
    tx.wait(1)

    print(f"Maximum WETH held: {flash_contract.maxTest()}")
    print(f"Was token0: {flash_contract.testToken0()}")
    print("....\n\n")

    ###  Meercat Exchange
    print(f"Initiating flash loan test with Meerkat...")
    # Going with .0022 - with a .0002 fee extra - even though config says .002 fee
    tx = flash_contract.initiateWethFlashloan(
        "0x32481a0466e66eE80e9d50A0DA120f8D16041787",
        True,
        (13 * (10**18)),
        ((13 + (13 * 0.0022)) * (10**18)),
    )
    tx.wait(1)

    ### Testing 3xcalibur -- contracts are unverified but fee is either .000369 or .00369 -- I'll try .001 first
    ### .001 failed.  .0038 (~.0002 over the .00369 fee) succeeded
    print(f"Initiating flash loan test with 3xcalibur...")
    tx = flash_contract.initiateWethFlashloan(
        "0xA84861b2Ccce56c42f0EE21E62b74E45d6F90C6d",
        True,
        (3 * (10**18)),
        ((3 + (3 * 0.0038)) * (10**18)),
    )
    tx.wait(1)

    print(f"Maximum WETH held: {flash_contract.maxTest()}")
    print(f"Was token0: {flash_contract.testToken0()}")
    print("....\n\n")

    # ### get whatever WETH we didn't use back
    # print("Getting the wETH back...")
    # recover_weth(account, flash_contract)


if __name__ == "__main__":
    main()
