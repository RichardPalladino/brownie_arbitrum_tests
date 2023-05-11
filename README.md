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