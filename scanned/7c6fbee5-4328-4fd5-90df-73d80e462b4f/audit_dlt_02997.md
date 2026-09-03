# [?] FoxLpBondsPool - Stale _stakeAmount from manipulable AMM spot quote

## Summary
Severity: Unknown
Chain: EVM
Component: FoxLpBondsPool
Published: 2026-08-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/FoxLpBondsPool_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~112,976.12 USDC (~$118.7K reported)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// FOX / FoxLpBondsPool — AMM-spot-priced LP bond mint manipulation — BNB Chain
// ~$113K (112,976 USDT + dust) drained by an attacker-controlled contract in a single tx.
//
// Exploit tx  : 0x8e1775cbfd44db29744cc6687ff1822d2c47321de6e94062f789ad6181ad5514 (block 116169049)
// Caller EOA  : 0x5670d36f00bc7F6860B6AfdDb288E3668efc0ef9 (nonce 393, plain EOA, tx.origin)
// Attack ctrt : 0x3A82A2A77061017927e5331fFFd07c0308a1D2DA (entry, selector 0x7f14cf11)
// Helper ctrt : 0x9fa6d8a13b35e051bfc145918db0111dec13d1a0 (stake/bond orchestrator, passed as arg)
// Victim pair : 0xaAB18BCdEE287AeA288c0560612CAADF7c328803 (PancakeSwap USDT/FOX pair)
//   FOX token : 0xdF81d50c6657487D19B66A1b5375E35A804Abb93
//   USDT (BSC): 0x55d398326f99059fF775485246999027B3197955 (18 decimals)
// FoxLpBondsPool: 0x58e2a853bB14e46bEFD3148bd4280370feA4655a
// Treasury      : 0x87614d97808dCdecB069fe8489848Fa1c001e04D
//
// Root cause (reproducible contract mechanism, verified against the on-chain trace, NOT a
// key/signer/privileged-claim compromise):
//   FoxLpBondsPool.stake() reads a _stakeAmount from a manipulable PancakeSwap AMM spot quote of
//   the USDT/FOX pair BEFORE the flow executes its own large USDT->FOX swap against that same pair.
//   The swap materially skews the pair reserves. The subsequent addLiquidity() then supplies FOX
//   and USDT at the now-different reserve ratio, but _stakeAmount is never recomputed from the
//   assets actually deposited or the fair value of the minted LP. Treasury.lpBonds() trusts the
//   stale, economically-unsupported _stakeAmount, mints FOX against it, and in the same flow
//   transfers an inviterRewardAmount of freshly-minted FOX to an attacker-controlled referral
//   address. The attacker then sells that FOX back into the pair in the same tx for USDT.
//   Everything is funded by a large multi-pool USDT flash-loan aggregation; the flash liquidity
//   only sets the scale, it is not the vulnerability. The defect is manipulable spot pricing +
//   no accounting-to-actual-backing validation + immediate (non-delayed) reward settlement.
//
// Trace evidence (receipt logs, USDT/FOX are 18 decimals):
//   - log 62 : helper sends 240,987,392 USDT into the pair  (USDT->FOX swap, skews reserves)
//   - log 64 : helper receives    490,357 FOX from that swap
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/FoxLpBondsPool_exp.sol_
