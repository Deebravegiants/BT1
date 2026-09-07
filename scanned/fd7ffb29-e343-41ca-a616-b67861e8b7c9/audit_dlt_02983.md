# [?] MOKE - Unprotected claim() drained via EIP-7702 self-delegation

## Summary
Severity: Unknown
Chain: EVM
Component: MOKE
Published: 2026-08-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/MOKE_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~1546.44 BNB (~$907.7K)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// MOKE (Moke) - unprotected public `claim()` mints protocol-reserve MOKE to any caller,
//               laundered to BNB through the project's own LP manager + dividend vault.
// BNB Chain. ~$907.7K reported loss (TenArmor). No public root-cause writeup at build time;
// mechanism below was recovered by tracing the exploit tx from scratch.
//
// Exploit tx : 0x0776048b1b58064fb31b6513721811e7b44d6bdbe7bf5833158b241ca6756a8f
//              block 113652609, tx index 26.
//
// Attacker packaging (EIP-7702): the tx has `to == from == 0xE454...DCF8a`. That EOA had a
// 7702 delegation designator (0xef0100 || 0xc7fdea02...) installed in an EARLIER block and
// revoked later, so at the fork block the attacker EOA "is" its own exploit contract. This is
// the attacker delegating their OWN account to their OWN code and self-signing it - NOT a
// stolen key, compromised signer, admin role, or governance/proxy upgrade. Every victim call
// below is a plain public function reached by attacker-controlled state.
//
// Root cause (the actual bug):
//   MokeReleaseContract 0x684d722e (unverified; it IS MokeToken.releaseContract()) exposes a
//   PUBLIC `claim()` (payable, ~0.000341 BNB fee). Each call pulls a large fixed slice of the
//   MOKE sitting in the protocol's internal reserve pool (0x89715a07) straight to msg.sender
//   via MokeToken.releaseFromPair(caller, ~41.68M) + addReleasedBalance(caller, ~41.68M), with
//   NO check that the caller is entitled to that allocation. The attacker calls claim() 4x and
//   walks off with ~166M MOKE minted from reserves for a few tenths of a cent in fees.
//
// Cash-out path (all public, all the project's own plumbing):
//   - Moolah (Lista Lending) 0x8f73b65b flash-loans WBNB (403,344) + BTCB (3,169) for working
//     capital; Venus (vBTC/vBNB) is used to lever the BTCB into BNB.
//   - MokeLPManager 0xacabe59b removeLiquidity() unwinds the attacker's own pre-seeded LP.
//   - The stolen "released" MOKE can only move to whitelisted handlers, so it is fed into
//     MokeLPDividend 0x5ae569d8: distributeDividend() swaps the vault's MOKE to BNB and bumps
//     totalDividendPerLP, then claimDividend() is run across the 100 seeded holder accounts to
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/MOKE_exp.sol_
