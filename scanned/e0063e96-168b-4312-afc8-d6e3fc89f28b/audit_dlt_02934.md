# [?] Joe Agent - Reentrancy in removeLiquidityViaContract

## Summary
Severity: Unknown
Chain: BNB Chain
Component: JoeAgent
Published: 2026-05-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/JoeAgent_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$45K USD (62.5 BNB + ~1.196M JOE)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$45K USD (62.5 BNB + ~1,195,918 JOE)
// Attacker : 0xaa761779945dcc5f26064fc6dcb36ffab6ac7610
// Attack Contract : 0x31F81FCD91025728F24bD6f0E4EfB156e345A4CF
// Vulnerable Contract : 0xef0f12d08d66e76E1866e60F30a0DaA578e00c04 (Joe Agent / JOE, ERC1967 proxy)
// Implementation : 0xb12ce0a21f67a9fc3c8ad1c7dbc4b017b7e67319
// Attack Tx : 0xd16a1c3dcd84427b2c7dcccbe1854c1c5bf65900460e1a44a95c1aaaf140c3a5
// @Analysis
// Attack date: May 27, 2026
// Chain: BSC, Block: 100812531
// SlowMist: https://x.com/SlowMist_Team/status/2059887450663551352

// Root Cause:
// Joe Agent lets a user park LP inside the token contract (zapNativeForLP / addLiquidityViaContract),
// tracked per-user in lpInfo[user].lpAmount. removeLiquidityViaContract(liquidity,...) pulls that LP
// out of PancakeSwap, unwraps the WBNB and forwards the BNB to the user with a low-level call --
// and only updates lpInfo[user].lpAmount AFTER that external call (violating checks-effects-interactions).
//
// Because lpInfo is still un-zeroed when the BNB lands, the attacker's receive() re-enters
// removeLiquidityViaContract with the SAME liquidity value over and over. Each re-entry passes the
// `liquidity <= lpInfo[user].lpAmount` check and burns a fresh slice of LP -- but that LP belongs to
// the whole pool of depositors, not the attacker. ~25 nested calls drain 25 x 2.5 = 62.5 BNB (plus the
// JOE side of every burned LP) against a single ~437 LP position that the attacker only paid for once.
//
// Function selectors:
// 0x7cc112a6: zapNativeForLP(address,uint256,uint256,uint256,uint256)        -- deposit BNB -> LP position
// 0xacff149d: removeLiquidityViaContract(uint256,uint256,uint256,uint256)    -- vulnerable withdraw
// 0x11067f6a: lpInfo(address)                                                -- (lpAmount, lastAddLpTime)

interface IJoeAgent is IERC20 {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/JoeAgent_exp.sol_
