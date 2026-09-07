# [?] JulSwap - Flash Loan

## Summary
Severity: Unknown
Chain: BNB Chain
Component: JulSwap
Published: 2021-05-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/JulSwap_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1.5M

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 1.5M
// Attacker : https://bscscan.com/address/0xc3bc29941677db01b9645f7b8b72d27e3ba75372
// Attack Contract : https://bscscan.com/address/0x7c591aab9429af81287951872595a17d5837ce03
// Vulnerable Contract : https://bscscan.com/address/0x32dffc3fe8e3ef3571bf8a72c0d0015c5373f41d
// Attack Tx : https://bscscan.com/tx/0x1751268e620767ff117c5c280e9214389b7c1961c42e77fc704fd88e22f4f77a

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0x32dffc3fe8e3ef3571bf8a72c0d0015c5373f41d#code

// @Analysis
// Post-mortem :
// Twitter Guy :
// Hacking God :
pragma solidity ^0.8.0;

interface IBNBRouter {
    function swapExactTokensForBNB(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
    function swapBNBForExactTokens(
        uint256 amountOut,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external payable returns (uint256[] memory amounts);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/JulSwap_exp.sol_
