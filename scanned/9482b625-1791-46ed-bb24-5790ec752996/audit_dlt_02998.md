# [?] LpdFi (LOOPSDAO) - Spot-price manipulation + issue-boundary interest exploit

## Summary
Severity: Unknown
Chain: EVM
Component: LpdFi
Published: 2026-08-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/LpdFi_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~573,034.79 USDC net attacker gain (LpdFi paid out ~700,535 USDC + 4,059,427 LPD, burned 1,678,049 Cake-LP)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// LpdFi (LOOPSDAO) - spot-price oracle manipulation lets an attacker mint an inflated
//                    interest-bearing principal, then drain protocol-owned Cake-LP.
// BNB Chain. ~$573K attacker net gain. Root cause per DarkNavy writeup, verified below by
// tracing the two on-chain txs from scratch.
//
// Setup tx : 0xbb5b8573d7203e00f8fb9d4839dbeea46a8efd367eac8bed81e4ece2341c3588
//            block 113613923, ts 1785686399 (2026-08-02 15:59:59 UTC).
// Claim tx : 0x70bbe0aa3c7ef149ecb6128a06025885deaa8fef3f393a505d447d28ab3315d6
//            block 113613924, ts 1785686400 (2026-08-02 16:00:00 UTC), exactly 1 second later.
//
// Both txs are plain calls from the attacker EOA into the attacker's own pre-deployed executor
// contract (to != from, so NO EIP-7702). Every victim entrypoint the executor reaches is a
// permissionless public function - LpdFi.buy(uAmount), LpdFi.claimInterest(index), and
// PancakeSwap swaps. No signer, admin role, governance, or proxy upgrade is involved. Verified
// against the trace: the attacker EOA simply funds the executor with 116,495 USDC and calls it
// twice.
//
// Root cause (the actual bug):
//   - Lpd.price() values the LPD token from the INSTANTANEOUS reserves of a thin PancakeSwap
//     LPD/USDC pair (0x85346d31...). No TWAP, no liquidity floor, no deviation bound.
//   - LpdFi.buy(uAmount) lets the caller name a nominal USDC principal and uses that manipulable
//     spot price only to size the LPD deposit. Push LPD spot up ~5,163x and the LPD deposit
//     required to register a 140,324,732 USDC principal collapses to ~214,171 LPD.
//   - getOrder() accrues interest from the discrete (issue - lastIssue) index difference, not
//     elapsed wall time. Crossing the daily issue boundary after just 1 second credits a full
//     0.5% period: 140,324,732 * 0.5% = 701,623.66 USDC of "interest".
//   - claimInterest() funds that entitlement by removing protocol-owned Cake-LP with both
//     PancakeRouter min-outputs set to zero.
//
// Attack (executed by the executor bytecode, replayed here verbatim):
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-08/LpdFi_exp.sol_
