# [?] Saturn Protocol - Vulnerability Disclosure

## Summary
Severity: Unknown
Chain: Ethereum
Component: SaturnProtocol
Published: 2026-04-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SaturnProtocol_exp.sol
Type: defi-exploit-poc

## Details
Lost: 0 (Disclosure only; no exploit occurred)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// @KeyInfo — Vulnerability Disclosure (unpatched, no historical exploit)
// Protocol      : Saturn Protocol — StakedUSDat (sUSDat) ERC4626 vault
// Chain         : Ethereum Mainnet
// TVL at Risk   : ~$35.7M USD (DeFiLlama, 2026-04-14)
// Severity      : SAT-001 Critical | SAT-002 High
// Date Found    : 2026-04-14
// Researcher    : Innora Security Research (feng@innora.ai)
// Full Report   : https://gist.github.com/sgInnora/b70ad98327649ed4ab976a122f45e485
// Twitter       : https://x.com/Innora_sg/status/2043979131617194043

// @Vulnerability SAT-001 — Withdrawal Freeze via Arithmetic Underflow
//   convertFromStrc() panics when strcBalance < getUnvestedAmount().
//   Triggered by processing queued redemptions after distributing rewards
//   (routine operations — no malicious actor required).
//   Effect: all withdrawals frozen for up to 30 days (vestingPeriod);
//   indefinitely if transferInRewards() is called again during the freeze.

// @Vulnerability SAT-002 — PROCESSOR Extracts up to 33.33% per Conversion
//   _validateConversion() applies toleranceBps=2000 (20%) independently to
//   BOTH price and amount checks. Compound effect: 1 - (0.8/1.2) = 33.33%
//   extraction rate per convertFromUsdat() call.
//   PROCESSOR_ROLE: 0x09d6e34ce24d54890ff0bc6a090b5f880f8c729f

// @Contracts
//   sUSDat Proxy : 0xD166337499E176bbC38a1FBd113Ab144e5bd2Df7
//   sUSDat Impl  : 0x2005e0ca201a37694125ff267ae57872bea0a0ce
//   SwapFacility : 0xB6807116b3B1B321a390594e31ECD6e0076f6278
//   USDat        : 0x23238f20b894f29041f48D88eE91131C395Aaa71
//   WithdrawQueue: 0x4Bc9FEC04F0F95e9b42a3EF18F3C96fB57923D2e

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/SaturnProtocol_exp.sol_
