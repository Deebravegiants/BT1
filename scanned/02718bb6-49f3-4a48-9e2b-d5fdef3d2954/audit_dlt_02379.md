# [?] DDCoin - Flashloan attack and smart contract vulnerability

## Summary
Severity: Unknown
Chain: BNB Chain
Component: DDCoin
Published: 2023-06-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/DDCoin_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$300k
References:
- https://twitter.com/ImmuneBytes/status/1664239580210495489
- https://twitter.com/ChainAegis/status/1664192344726581255?cxt=HHwWjsDRldmHs5guAAAA

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~300K USD$
// Attacker : https://bscscan.com/address/0x0a3fee894eb8fcb6f84460d5828d71be50612762
// Attack Contract : https://bscscan.com/address/0x105e9b0266ae0ae670b7fe9af08cf32049f0dd21
// Vulnerable Contract : https://bscscan.com/address/0xb3a636ac4c271e6cd962cad98eae9cf71f5a49c8
// Attack Tx : https://bscscan.com/tx/0xd92bf51b9bf464420e1261cfcd8b291ee05d5fbffbfbb316ec95131779f80809

// @Analysis
// https://twitter.com/ImmuneBytes/status/1664239580210495489
// https://twitter.com/ChainAegis/status/1664192344726581255?cxt=HHwWjsDRldmHs5guAAAA

interface IMarketPlace {
    struct SellListing {
        uint256 itemId;
        uint256 index;
        uint256 price;
        uint256 amount;
        uint256 time;
        address buyer;
        address seller;
    }

    function currenyId() external view returns (uint256);

    function inviteLimit(
        address
    ) external view returns (uint256);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/DDCoin_exp.sol_
