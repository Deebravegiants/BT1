# [?] EverValueCoin exploit (2025-08)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: EverValueCoin
Published: 2025-08
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/EverValueCoin_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 100k USD
// Attacker : https://arbiscan.io/address/0xaa06fde501a82ce1c0365273684247a736885daf
// Attack Contract : https://arbiscan.io/address/0x2fad746cfaaf68aa098f704fb6537b0a05786df8
// Vulnerable Contract : https://arbiscan.io/address/0x03339ecae41bc162dacae5c2a275c8f64d6c80a0
// Attack Tx : https://arbiscan.io/tx/0xb13b2ab202cb902b8986cbd430d7227bf3ddca831b79786af145ccb5f00fcf3f

// @Info
// Vulnerable Contract Code : https://arbiscan.io/address/0x03339ecae41bc162dacae5c2a275c8f64d6c80a0#code

// @Analysis
// Post-mortem : https://x.com/SuplabsYi/status/1961906638438445268
// Twitter Guy : https://x.com/SuplabsYi/status/1961906638438445268
// Hacking God : N/A
interface Iorderbook {
    function addNewOrder(bytes32 _pairId, uint256 _quantity, uint256 _price, bool _isBuy, uint256 _timestamp)
        external;
}

interface ISwapRouter {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/EverValueCoin_exp.sol_
