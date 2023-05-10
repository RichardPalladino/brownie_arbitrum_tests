# Testing forking and flash loans / swaps with Ethereum Brownie

1. Test whether I can fork Arbitrum and get some fake WETH.
2. Test whether I can fork Arbitrum, get, borrow, and repay some fake WETH (directly from any number of UniswapV2 compatible LPs).
3. Test forking Arbitrum, getting WETH, and performing a flash swap from WETH to some other currency (on a variety of DEX LPs).
    * Use a hook/callback function in the flash-swap client contract as the rudimentary foundation for future arbitrage activity.