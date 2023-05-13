// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import '../interfaces/IERC20.sol';
import '../interfaces/IwETH.sol';
import '../interfaces/IUniswapV2Pair.sol';

// Basic template contract I'll be working with
contract TestFlashLoan{
    address private owner;
    address private weth;
    address[] private lps = new address[](3);

    uint256 public maxTest;
    bool public testToken0;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // modifier to confirm the callback/hook is only from a permissioned pool during the transaction
    modifier approvedLP() {
        require((
            (msg.sender == lps[0]) 
            || (msg.sender == lps[1]) 
            || (msg.sender == lps[2])
            ), "wrong LP");
        _;
    }

    constructor(address _weth) {
        owner = msg.sender;
        weth = _weth;
    }

    function recoverERC20(uint256 _amount, address _token) external {
        require(_amount > 0, "0 xsfr");
        require(_token != address(0), "0 address");
        require(IERC20(_token).balanceOf(address(this)) >= _amount, "insuf bal");
        IERC20(_token).transfer(owner, _amount);
    }

    function newOwner(address _newOwner) external onlyOwner {
        owner = _newOwner;
    }

    function withdrawAll() external {
        payable(owner).transfer(address(this).balance);
    }

    function initiateWethFlashloan(
        address _LP, 
        bool _isToken0, 
        uint256 _loanAmnt, 
        uint256 _wethToRepay) external {

            require(_loanAmnt != 0);
            lps[0] = _LP;
            IUniswapV2Pair lp = IUniswapV2Pair(_LP);

            // testToken0 = _isToken0;
            // maxTest = IwETH(weth).balanceOf(address(this));



            if(_isToken0 == true){
                lp.swap(_loanAmnt, 0, address(this), abi.encode(_wethToRepay));
            } else {
                lp.swap(0, _loanAmnt, address(this), abi.encode(_wethToRepay));
            }

    }

    /* // from another contract
    struct CallbackData {
    address debtPool;
    address targetPool;
    bool debtTokenSmaller;
    address borrowedToken;
    address debtToken;
    uint256 debtAmount;
    uint256 debtTokenOutAmount;
    }
    */

    function _execute(
        address _sender,
        uint _amount0,
        uint _amount1,
        bytes memory _data
    ) internal {
        // obtain an amount of token that I pulled int
        uint amountToken = _amount0 == 0 ? _amount1 : _amount0;

        // (address sourceRouter, address targetRouter) = abi.decode(_data, (address, address));
        (uint256 _repayAmnt) = abi.decode(_data, (uint256));
        require(_repayAmnt !=0);

        IwETH wethContract = IwETH(weth);
        maxTest = wethContract.balanceOf(address(this));
        
        wethContract.transfer(msg.sender, _repayAmnt);


        // IUniswapV2Pair iUniswapV2Pair = IUniswapV2Pair(msg.sender);
        // address token0 = iUniswapV2Pair.token0();
        // address token1 = iUniswapV2Pair.token1();

        // require(token0 != address(0) && token1 != address(0), 'e11');

        // // if _amount0 is zero sell token1 for token0
        // // else sell token0 for token1 as a result
        // address[] memory path1 = new address[](2);
        // address[] memory path2 = new address[](2);

        // address forward = _amount0 == 0 ? token1 : token0;
        // address backward = _amount0 == 0 ? token0 : token1;

        // // path1 represents the forwarding exchange from source currency to swapped currency
        // // path1[0] = path2[1] = _amount0 == 0 ? token1 : token0;
        // path1[0] = path2[1] = forward;
        // // path2 represents the backward exchange from swapeed currency to source currency
        // // path1[1] = path2[0] = _amount0 == 0 ? token0 : token1;
        // path1[1] = path2[0] = backward;

        // IERC20 token = IERC20(forward);
        // token.approve(targetRouter, amountToken);

        // // calculate the amount of token how much input token should be reimbursed, BNB -> BUSD
        // uint amountRequired = IUniswapV2Router(sourceRouter).getAmountsIn(amountToken, path2)[0];

        // // swap token and obtain equivalent otherToken amountRequired as a result, BUSD -> BNB
        // uint amountReceived = IUniswapV2Router(targetRouter).swapExactTokensForTokens(
        //     amountToken,
        //     amountRequired, // we already now what we need at least for payback; get less is a fail; slippage can be done via - ((amountRequired * 19) / 981) + 1,
        //     path1,
        //     address(this), // its a foreign call; from router but we need contract address also equal to "_sender"
        //     block.timestamp + 60
        // )[1];

        // // fail if we didn't get enough tokens
        // require(amountReceived > amountRequired, 'e13');

        // IERC20 otherToken = IERC20(backward);

        // // callback should send the funds to the pair address back
        // otherToken.transfer(msg.sender, amountRequired); // send back borrow
        // // transfer the profit to the contract owner
        // otherToken.transfer(owner, amountReceived - amountRequired);
    }


    /* 
    -------------------------------------------
    CALLBACK (and fallback) FUNCTIONS
    -------------------------------------------
    */

    // Sushiswap and Arbidex should both use the standard callback function
    // https://arbidex.gitbook.io/arbitrum-exchange/arbidex-classic/token-swap
    function uniswapV2Call(
        address sender,
        uint256 amount0,
        uint256 amount1,
        bytes memory data
    ) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // From SolidLizard ICallee interface https://github.com/SolidLizard/SolidLizard-Contracts/blob/master/contracts/interface/ICallee.sol
    // function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) 
    // Ramses exchange also uses the "hook" pattern, apparantly from Solidly forked code https://docs.ramses.exchange/resources/deployed-contract-addresses
    // function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external
    function hook(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // Arbidex uses an abnormal hook/callback https://arbidex.gitbook.io/arbitrum-exchange/security/contracts
    // https://arbiscan.io/address/0xA6efAE0C9293B4eE340De31022900bA747eaA92D#code
    // function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external
    function arbdexCall(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // Of course zyberswap has to do it different too https://docs.zyberswap.io/security/smart-contracts
    // https://arbiscan.io/address/0x95D19380c9f77e75f4D3d3d38cC6A34e756c67fb#code
    // function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;
    function ZyberCall(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // TraderJoe XYZ has a different callback https://github.com/traderjoe-xyz/joe-core/tree/main
    // Swap function is standard
    function joeCall(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // Meerkat Finance is different https://mmfinance.gitbook.io/arbitrum/contract-and-security/contracts
    // https://arbiscan.io/address/0x0653766Fc1A790D49c3819F838B4Fe1510B7B862#code
    // function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) 
    function MeerkatCall(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // xcalibur doesn't have verified docs, but does appear to match the hook function like Solidly forks of SolidLizard, etc.
    //  https://3six9innovatio.gitbook.io/documentation/contracts/official-3xcalibur-contracts

    // Sterling Finance also uses hook https://sterling-finance.gitbook.io/welcome/ 
    // https://arbiscan.io/address/0xF73F93FBf26BcCc89AE9A7fd12A6eb4D4D7aF783#code
    // function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) 

    // AlienFi is based on PancakeSwap https://alien-2.gitbook.io/alien-finance/
    // https://arbiscan.io/address/0xB8aA98969728eAd6076FE9a72cAB65CeA5DEe023#code
    // Standard: swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) external lock {
    function pancakeCall(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // OreoSwap has it's own swap callback https://github.com/oreoswap/
    // https://arbiscan.io/address/0xF76519bfd4BDA679a13C562e94ABaB0a900603a5#code
    // Standard UniswapV2 contracts swap(uint amount0Out, uint amount1Out, address to, bytes calldata data) 
    function OreoSwapCall(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }

    // Stargate swap -- https://stargateprotocol.gitbook.io/stargate/v/user-docs/  and https://stargateprotocol.gitbook.io/stargate/
    // Doesn't appear to follow the UniswapV2 pool/pair swap function standards https://arbiscan.io/address/0xaa4BF442F024820B2C28Cd0FD72b82c63e66F56C#code
    // function swap(uint16 _dstChainId, uint256 _dstPoolId, address _from,vuint256 _amountLD, uint256 _minAmountLD, bool newLiquidity) external nonReentrant onlyRouter 
    // I don't think Stargate will work other than through the router -- this should be accounted for in the triad generation script

    // Arbswap -- https://github.com/Arbswap-Official
    // function swap(uint amount0Out, uint amount1Out, address to, bytes calldata data)
    function swapCall(address sender, uint amount0, uint amount1, bytes calldata data) external approvedLP {
        _execute(sender, amount0, amount1, data);
    }


    // @dev Redirect uniswap callback function
    // The callback function on different DEX are not same (as seen above), so use a fallback to redirect to uniswapV2Call
    fallback(bytes calldata _input) external returns (bytes memory) {
        (address sender, uint256 amount0, uint256 amount1, bytes memory data) = abi.decode(_input[4:], (address, uint256, uint256, bytes));
        _execute(sender, amount0, amount1, data);
    }


    receive() external payable {}

}