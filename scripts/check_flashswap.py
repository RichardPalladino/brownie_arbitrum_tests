from brownie import interface, config, network, TestFlashSwap
from scripts.helper_scripts import get_account
from web3 import Web3


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


def deploy_flashswap(_account, _weth):
    print(f"Deploying the FlashTemplate contract to {network.show_active()}")
    contract = TestFlashSwap.deploy(
        _weth,
        {"from": _account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Contract deployed successfully to {contract.address}")
    print("....\n\n")
    return contract


def calculate_out(_LP, _token_in, _a_in, _fee):
    lp = interface.IUniswapV2Pair(_LP)
    erc20 = interface.IERC20(_token_in)  # do I even need to do this?

    token0 = True if lp.token0() == _token_in else False
    reserves = lp.getReserves()
    decimals = erc20.decimals()  # ?  is this even needed
    reserves0 = reserves[0]
    reserves1 = reserves[1]
    k = reserves0 * reserves1

    if token0:
        # calculate base to quote swap, with fees
        a_out = (reserves1 - (k / (reserves0 + _a_in))) * _fee
    else:
        # calculate quote to base swap, with fees
        a_out = (reserves0 - (k / (reserves1 + _a_in))) * _fee

    print(f"{_a_in} of {_token_in} into {_LP}, and {a_out} out")
    return a_out


def main() -> None:
    weth_contract = interface.IwETH(
        config["networks"][network.show_active()]["weth_token"]
    )

    print(f"Connected: {network.is_connected()}")
    account = get_account()

    flash_contract = deploy_flashswap(account, weth_contract)

    print("Getting wETH....")
    get_weth(account, 5)

    print(f"Transferring wETH to contract {flash_contract.address}")
    transfer_weth_to(account, flash_contract.address, 5)

    ## Testing 3xcalibur -- contracts are unverified but fee is either .000369 or .00369 -- I'll try .001 first
    ## .00369 is the likely fee
    print("Swapping .5 WETH for ARB on 3xcalibur")
    lp = "0xA84861b2Ccce56c42f0EE21E62b74E45d6F90C6d"
    amount_out = calculate_out(lp, weth_contract, (0.5 * (10**18)), (1 - 0.00369))

    flash_contract.swapWETH(lp, (0.5 * (10**18)), ((1 - 0.00369) * 100000))
    print(f"Test calculating out: {flash_contract.aOut()}")
    arb_balance = interface.IERC20(
        "0x912CE59144191C1204E64559FE8253a0e49E6548"
    ).balanceOf(flash_contract.address)
    print(f"Contract's ARB balance: {arb_balance}")

    ## Testing ArbSwap
    ## .003 is the likely fee
    print("Swapping .5 WETH for USDC on ArbSwap")
    lp = "0x6E8AEE8Ed658fDCBbb7447743fdD98152B3453A0"
    amount1_out = calculate_out(lp, weth_contract, (0.5 * (10**18)), (1 - 0.003))

    flash_contract.swapWETH(lp, (0.5 * (10**18)), ((1 - 0.003) * 100000))
    print(f"Test calculating out: {flash_contract.aOut()}")
    usdc_balance = interface.IERC20(
        "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
    ).balanceOf(flash_contract.address)
    print(f"Contract's USDC balance: {usdc_balance}")

    ## Testing LizardSwap
    ## .005 is the max fee
    print("Swapping .5 WETH for USDC on SolidLizard")
    lp = "0xe20F93279fF3538b1ad70D11bA160755625e3400"
    amount2_out = calculate_out(lp, weth_contract, (0.5 * (10**18)), (1 - 0.006))

    flash_contract.swapWETH(lp, (0.5 * (10**18)), ((1 - 0.006) * 100000))
    print(f"Test calculating out: {flash_contract.aOut()}")
    usdc_balance = interface.IERC20(
        "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"
    ).balanceOf(flash_contract.address)
    print(f"Contract's USDC balance: {usdc_balance}")
    print(f"...with {usdc_balance - amount1_out} received this swap.")

    ## Testing ZyberSwap
    ## .0025 is the max fee
    print("Swapping .5 WETH for ARB on ZyberSwap")
    lp = "0x7dB09b248F026F1a77D58B56Ab92943666672968"
    amount3_out = calculate_out(lp, weth_contract, (0.5 * (10**18)), (1 - 0.0025))

    flash_contract.swapWETH(lp, (0.5 * (10**18)), ((1 - 0.0025) * 100000))
    print(f"Test calculating out: {flash_contract.aOut()}")
    arb_balance = interface.IERC20(
        "0x912CE59144191C1204E64559FE8253a0e49E6548"
    ).balanceOf(flash_contract.address)
    print(f"Contract's ARB balance: {arb_balance}")
    print(f"...with {arb_balance - amount_out} received this swap.")


if __name__ == "__main__":
    main()
