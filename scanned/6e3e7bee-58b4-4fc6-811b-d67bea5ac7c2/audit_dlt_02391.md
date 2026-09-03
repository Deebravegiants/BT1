# [?] Themis - Manipulation of prices using Flashloan

## Summary
Severity: Unknown
Chain: Arbitrum
Component: Themis
Published: 2023-06-28
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/Themis_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$370k
References:
- https://arbiscan.io/address/0x33f3fb58ea0f91f4bd8612d9f477420b01023f25
- https://twitter.com/BeosinAlert/status/1673930979348717570

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~370K USD$
// Attacker : https://arbiscan.io/address/0xdb73eb484e7dea3785520d750eabef50a9b9ab33
// Attack Contracts : https://arbiscan.io/address/0x05a1b877330c168451f081bfaf32d690ea964fca
// https://arbiscan.io/address/0x33f3fb58ea0f91f4bd8612d9f477420b01023f25
// Vulnerable Contract : https://arbiscan.io/address/0x75f805e2fb248462e7817f0230b36e9fae0280fc
// Attack Tx : https://arbiscan.io/tx/0xff368294ccb3cd6e7e263526b5c820b22dea2b2fd8617119ba5c3ab8417403d8

// @Analysis
// https://twitter.com/BeosinAlert/status/1673930979348717570
// Detailed attack steps: https://twitter.com/BlockSecTeam/status/1673897088617426946

interface IThemis {
    function supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode) external;

    function setUserUseReserveAsCollateral(address asset, bool useAsCollateral) external;

    function borrow(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        uint16 referralCode,
        address onBehalfOf
    ) external;
}

interface IGauge is IERC20 {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/Themis_exp.sol_
