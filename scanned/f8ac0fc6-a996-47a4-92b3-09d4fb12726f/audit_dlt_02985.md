# [?] Perpetual Protocol - Access Control / Missing Permission Check

## Summary
Severity: Unknown
Chain: Optimism
Component: PerpetualProtocol
Published: 2026-07-16
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/PerpetualProtocol_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~3,062 USDC

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Perpetual Protocol (v2 / Curie-style perp) — missing access-control guard on
// OrderBook.updateFundingGrowthAndLiquidityCoefficientInFundingPayment().
//
// Incident tx : 0xb0a8a3cc76fb17bf965ab1dee3b76b62f79ca72def31e12f8ad8b1711625df08
//   Optimism block 154311432, tx index 12.
//   Attacker EOA 0x957c6cF5E0F69597dB7A8065c94af1A48aBCA47d sends a CREATE (to == null):
//   the ENTIRE attack lives in the contract constructor, and the deployed runtime is a
//   bare `revert` stub. So the faithful replay is: deploy the exact creation bytecode
//   (init code + constructor args) at the pre-attack block and watch the vaults drain.
//
// Root cause:
//   OrderBook.updateFundingGrowthAndLiquidityCoefficientInFundingPayment() (OrderBook.sol:232)
//   is missing the _requireOnlyClearingHouse() guard that its sibling functions carry, so an
//   attacker can call it directly. The attacker (per market):
//     1. addLiquidity() a dust order (base=2, quote=1 wei) to create a cached liquidity entry,
//     2. calls the unguarded funding function with a fabricated twPremiumX96 =
//        0x0172ebad6ddc73c86d67c5faa71c245689c107950240... (~1e70) to poison the order's
//        cached funding growth,
//     3. settleAllFunding then produces a bogus ~1.46e36 funding payment that inflates the
//        account's realized PnL,
//     4. Vault.withdraw() cashes the fake PnL out as real USDC belonging to other LPs.
//   The single tx runs this against TWO perp deployments (two vaults) and forwards the loot
//   to the attacker EOA.
//
// Constructor args baked into the creation code (from the real tx input):
//   arg0  recipient EOA      0x957c6cF5E0F69597dB7A8065c94af1A48aBCA47d
//   arg1  settlement token   0x7F5c764cBc14f9669B88837ca1490cCa17c31607  (USDC.e, 6 dp)
//   uint256[5] market #1     [vault 0x28bb.., clearingHouse 0x4f79.., .., baseToken 0xab3f.., pool 0x66b0..]
//   uint256[5] market #2     [vault 0xf127.., clearingHouse 0x8098.., .., baseToken 0x28d8.., pool 0x059c..]
//   bool, bool               (true, true) — attack both markets
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/PerpetualProtocol_exp.sol_
