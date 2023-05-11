from brownie import accounts, network, config, interface
from web3 import Web3

LOCAL_BLOCKCHAIN_FORKS = ["arbitrum-main-fork"]
# LOCAL_BLOCKCHAINS = LOCAL_BLOCKCHAIN_FORKS + ["development", "ganache-local", "hardhat"]


def get_account(index=None, id=None) -> str:
    ### accounts[0]
    # accounts.add(env)
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() == "arbitrum-main-fork":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


# def get_lending_pool():
#     pool_addresses_provider = interface.ILendingPoolAddressesProvider(
#         config["networks"][network.show_active()]["lending_pool_addresses"]
#     )
#     lending_pool_address = pool_addresses_provider.getLendingPool()
#     lending_pool = interface.ILendingPool(lending_pool_address)
#     return lending_pool


def approve_erc20(spender, amount, erc20_address, account):
    print(f"Approving {spender} to spend up to {amount} of {erc20_address}")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


# def get_borrowable_data(lending_pool, account):
#     (
#         total_collateral_eth,
#         total_debt_eth,
#         available_borrow_eth,
#         current_liquidation_threshold,
#         ltv,
#         health_factor,
#     ) = lending_pool.getUserAccountData(account.address)
#     available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
#     total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
#     total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
#     print(f"You have {total_collateral_eth} worth of ETH deposited.")
#     print(f"You have {total_debt_eth} worth of ETH borrowed.")
#     print(f"You can borrow {available_borrow_eth} worth of ETH.")
#     return (float(available_borrow_eth), float(total_debt_eth))
