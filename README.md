# Testing forking and flash loans / swaps with Ethereum Brownie

1. Test whether I can fork Arbitrum and get some fake WETH.
    * Completed with the `network-config.yaml` file.  Run `brownie networks import ./network-config.yaml` to get the new network.
    * You can run `brownie networks import ./network-config.yaml true` if you already imported once and want to overwrite.
2. Test whether I can fork Arbitrum, get, borrow, and repay some fake WETH (directly from any number of UniswapV2 compatible LPs).
3. Test forking Arbitrum, getting WETH, and performing a flash swap from WETH to some other currency (on a variety of DEX LPs).
    * Use a hook/callback function in the flash-swap client contract as the rudimentary foundation for future arbitrage activity.


### Other notes
* Forking can also be done at specific block #'s with the following command lines as examples (the "@123456" is the block number)
    ```
    brownie networks add development chain-name-fork cmd=ganache-cli host=http://127.0.0.1 fork=RPC_URL@123456 accounts=10 mnemonic=brownie port=8545
    ```
    or
    ```
    npx hardhat node --fork https://eth-mainnet.alchemyapi.io/v2/<key> --fork-block-number 11095000
    ```
    if Hardhat is installed (as it is for me).
* As I have written it, this will require your Infura key in the .env file, per Brownie's standards.
* Potentially you can update the fork to be at a specific block, using an Arbitrum node provider's URL with the following code:
    ```
    brownie networks modify arbitrum-main-fork fork=RPC_URL@123456
    ```
    but I have not yet tested...
* I could write tests but this isn't a full project. Really it's just for me to play around with forking and flash loans/swaps using Brownie and the Arbitrum network.

# Further notes

weth: 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1
usdc: 0xff970a61a04b1ca14834a43f5de4533ebddb5cc8
dai: 0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1
usdt: 0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9
wbtc: 0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f

* Chronos exchange and other AMMs similar to UniswapV2 have good liquidity: https://chronos.exchange/ , https://arbiscan.io/address/0xafE909b1A5ed90d36f9eE1490fCB855645C00EB3
---- Add this factory 0xCe9240869391928253Ed9cc9Bcb8cb98CB5B0722 -- Chronos

* Stargate factory may match UniswapV2, but their LP contract is non-standard -- remove from the group

# Todo (now or later)
1. Finish validating the "max fees" for each DEX
2. Re-label "average_fee" to "max_fee"
3. Eventually be able to handle each DEX's dynamic or varying fees individually