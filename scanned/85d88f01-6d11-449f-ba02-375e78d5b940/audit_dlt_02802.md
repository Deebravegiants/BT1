# [?] UsualMoney - Arbitrage

## Summary
Severity: Unknown
Chain: Ethereum
Component: UsualMoney
Published: 2025-05-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/UsualMoney_exp.sol
Type: defi-exploit-poc

## Details
Lost: 43k USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

// @KeyInfo - Total Lost : 43k USD
// Attacker : https://etherscan.io/address/0x2ae2f691642bb18cd8deb13a378a0f95a9fee933
// Attack Contract : https://etherscan.io/address/0xf195b8800b729aee5e57851dd4330fcbb69f07ea
// Vulnerable Contract : https://etherscan.io/address/0x35d8949372d46b7a3d5a56006ae77b215fc69bc0
// Attack Tx : https://etherscan.io/tx/0x585d8be6a0b07ca2f94cfa1d7542f1a62b0d3af5fab7823cbcf69fb243f271f8


// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x35d8949372d46b7a3d5a56006ae77b215fc69bc0#code

// @Analysis
// Post-mortem : https://www.quadrigainitiative.com/hackfraudscam/usualmoneyusdssyncvaultpricingarbitrageexploit.php
// Twitter Guy : https://x.com/BlockSecTeam/status/1927601457815040283
// Hacking God : https://x.com/tonykebot/status/1927603610180788499


contract UsualMoney is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 22575930 - 1; 
    uint256 borrowAmount = 1899838465685386939269479;
     uint256 private uniV3TokenId;
  

    //Related contracts 
    IWETH constant WETH = IWETH(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IERC20 constant USD0Plus = IERC20(0x35D8949372D46B7a3D5A56006AE77B215fc69bC0);
    IERC20 constant USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 constant USD0 = IERC20(0x73A15FeD60Bf67631dC6cd7Bc5B6e8da8190aCF5);
    IERC20 constant sUSDS = IERC20(0xa3931d71877C0E7a3148CB7Eb4463524FEc27fbD);
    ICurvePool constant USD0USD0Pool = ICurvePool(0x1d08E7adC263CfC70b1BaBe6dC5Bb339c16Eec52);
    INonfungiblePositionManager constant UNI_V3_POS = INonfungiblePositionManager(0xC36442b4a4522E871399CD717aBDD847Ab11FE88);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/UsualMoney_exp.sol_
