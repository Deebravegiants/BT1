# [?] WUSD.fi - _englove Sybil Incentive Abuse

## Summary
Severity: Unknown
Chain: Ethereum
Component: WUSD
Published: 2026-05-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/WUSD_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$200K USD (GLOVE emissions + LP drain)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$200K USD (USDC + USDT drained from Uniswap V3 GLO pools)
// Attacker        : 0x88329A09428778F62BC0C8BAac0997864E5a57f8
// Vulnerable      : 0x068E3563b1c19590F822c0e13445c4FA1b9EEFa5 (WUSD - Wrapped USD, _englove reward path)
// Reward token    : 0x70c5f366db60a2a0c59c4c24754803ee47ed7284 (GLOVE / GLO)
// Attack Tx       : 0x2051c1f8d43730c41cc353b5dffd8cc59f96cb1ca56fdce4b28fb127bdb37712
// @Analysis
// Attack date : May 25, 2026
// Chain       : Ethereum, Block 25170426
// ExVul alert : https://x.com/exvulsec/status/2058803971947385330
//
// Root Cause:
// WUSD.wrap() pays a GLOVE reward via the internal _englove() routine:
//
//   function _englove(uint256 wrapping) internal {
//       uint256 gloves = IGlove(_GLOVE).balanceOf(msg.sender);
//       if (wrapping >= _MIN_GLOVABLE && gloves < _MAX_GLOVE) {
//           IGlove(_GLOVE).mintCreditless(msg.sender, Math.min(_MAX_GLOVE - gloves,
//               wrapping > 1_000e18 ? (_MAX_GLOVE * wrapping) / _EPOCH
//                                   : (_MID_GLOVE * wrapping) / 1_000e18));
//       }
//   }
//
// Eligibility depends ONLY on msg.sender's *current* GLOVE balance (gloves < _MAX_GLOVE = 2e18)
// and the wrap size (wrapping >= _MIN_GLOVABLE = 100e18). There is no per-address claim ledger,
// no cooldown, and no identity binding. A brand-new address always holds 0 GLOVE < _MAX_GLOVE,
// so it ALWAYS qualifies for a fresh ~2 GLOVE mint when it wraps >= 100,000 WUSD.
//
// The minted GLOVE is "creditless" (soulbound) and only vests into transferable "credited"
// GLOVE through unwrap()->_deglove(), proportional to how many global epochs elapsed since the
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/WUSD_exp.sol_
