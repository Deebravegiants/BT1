# [?] LULA - Reward recycle deflation manipulation via flash loan

## Summary
Severity: Unknown
Chain: EVM
Component: LULA
Published: 2026-07-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/LULA_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~578K USDT

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// LULA — flash-loan-amplified reward-recycle self-drain on BNB Chain
// ~$578K (578,295 USDT) drained from the LULA/USDT PancakeSwap pair in a single tx.
//
// Exploit tx : 0xa219ab9d57e520e5235b15a8801f4ebac8cc45551be0430ce4e49caea0411d7c (block 112655390)
//   Direct CALL (non-empty `to`): the attacker EOA calls its OWN already-deployed helper
//   contract 0x5E50...A816 with selector 0x763a0e5b(uint256=15000000), forwarding 1e10 wei.
//   The whole flash-loan + swap + claim/recycle loop runs inside that helper.
//
// Root cause (reproducible contract mechanism, NOT a key/signer/privileged-claim compromise):
//   Weeks before the drain the attacker deployed helper/clone contracts and, in EARLIER
//   transactions (~12 days prior), accumulated referral/team "reward" credit inside the LULA
//   token's reward bookkeeping. LULA's reward payout scales with how deflated the LULA/USDT
//   pool is. In the exploit tx the helper flash-loans a large USDT amount, swaps it to sweep
//   LULA out of the pair (maximizing the pool's deflation), then calls the PUBLIC
//   claimReward() -> recycle() path. Because the pre-accumulated reward now redeems against a
//   drained pool, it pays out far more USDT than was ever deposited. The helper repays the
//   flash loan and the attacker EOA nets ~578K USDT. Every step is a public function driven by
//   attacker-controlled on-chain state — no owner key, no privileged signer, no admin call.
//
// The attacker is a plain EOA (code == 0x at the fork block) calling a contract it itself
// deployed, so the faithful reproduction is to fork at the exploit block (where the ~12-day
// pre-accumulated reward state and helper/clone contracts already exist on-chain) and re-issue
// the exact original calldata, pranking the attacker EOA as both msg.sender and tx.origin.
// Calldata and value are hardcoded below (no env vars). We do NOT re-run the 12-day setup.
//
// LULA token   : 0xf5d7029eb6751d170dcF0Bb1c87Af6f93d5A2e9a ("LULA")
// LULA/USDT LP : 0xf0b36389a12a28be1280c0eC2a4bbc76889d6a96 (victim, PancakeSwap pair, drained)
// USDT         : 0x55d398326f99059fF775485246999027B3197955 (18 decimals on BSC)
// Attacker EOA : 0x2677806d48325Ced7533C54B86eD5e99b129a4ED (pure EOA)
// Helper       : 0x5E506Ba06Fa6C61D1069B0E68d7013DE35AFA816 (attacker contract, on-chain)
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/LULA_exp.sol_
