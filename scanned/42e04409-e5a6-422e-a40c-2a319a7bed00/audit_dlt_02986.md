# [?] Pro Token - Reward-on-transfer self-dealing winner drain

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ProToken
Published: 2026-07-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/ProToken_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~605K USDT (single tx; ~$8.2M cumulative across ~13 txs)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Pro Token (CryptoDAO / CDAO ecosystem) — reward-swap self-dealing drain on BNB Chain
// ~605K USDT drained from the USDT/Pro PancakeSwap LP in this single tx (the incident's
// ~$8.2M is the cumulative total across ~13 such transactions).
//
// Exploit tx : 0xaaea183bdb5d7e4fd3c8da1d5bfe7edcb2e1db2458cef9a3adac54db6a7793d1 (block 112654014)
//   Direct CALL (non-empty `to`): the attacker EOA calls its own already-deployed helper
//   contract 0xf00b... with selector 0x452ae331. The whole loop runs inside that helper.
//
// Root cause (reproducible contract mechanism, not a key compromise):
//   The Pro token's transfer logic auto-processes a "reward" on transfers involving its
//   registered player/holder addresses: it skims a 2.5% cut, then swaps the remainder of the
//   moved Pro into USDT through the USDT/Pro pair and forwards that USDT straight to a
//   "winner" address. The winner is one of the attacker-controlled addresses. By looping a
//   dust Pro transfer out of an attacker "player" clone (CLONE_A) ~300 times, the helper
//   repeatedly triggers the reward swap, each pass shipping ~2,016 USDT out of the pair to a
//   rotating trio of attacker "winner" addresses until the pair's USDT reserve is drained.
//   Nothing here is privileged — any address can register as a player and drive the loop.
//
// Pro token   : 0x8D65744527f55d0b2338350912d5C99A81ddF0e2 ("Pro Token")
// USDT/Pro LP : 0x63844BD4BFad910B1643713302a1cC1ed20d50c3 (victim, PancakeSwap pair, drained)
// USDT        : 0x55d398326f99059fF775485246999027B3197955 (18 decimals on BSC)
// Attacker EOA: 0x427671b2C8e91034A91FE698F9B7259b2345F45D
// Helper      : 0xf00bC28D22d71Be74Bc8aB0d11Fe77F6D77850ac (attacker contract, on-chain)
// Winners     : 0x4e94c21C.., 0xD9c854ED.., 0xc3994bFF.. (attacker-controlled, hold the USDT)
//
// Forensic replay: the helper contract, the player clones and the winner addresses all already
// exist on-chain at the fork block, so the faithful reproduction is to re-issue the exact
// original calldata against the deployed helper, pranking the attacker EOA as both msg.sender
// and tx.origin. The calldata is hardcoded below (no env vars).
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/ProToken_exp.sol_
