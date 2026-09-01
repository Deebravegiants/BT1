# [M] Invalid gossiped blocks bypass peer misbehavior scoring

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-11
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-8hh2-hrf2-cqf4
Type: github-advisory

## Details
| Field | Content |
|---|---|
| Severity |  Medium |
| CVSS 3.1 | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L` = 5.3 (Medium). |
| CWE | CWE-253 (Incorrect Check of Function Return Value) / CWE-704 (Incorrect Type Conversion), with the security-relevant effect being a bypassed CWE-693 (Protection Mechanism Failure) on the ban control. |
| Affected versions | <=v6.2.3 |
| Patched versions | 6.3.0 |
| Reporter credit | evan-forbes |
| GHSA | GHSA-8hh2-hrf2-cqf4 |

## Am I affected

You are affected if all of the following hold:

- You run Zebra v2.3.0 through v6.2.3.
- Your node processes block gossip (the default for a participating node).
- No special configuration is required. The default configuration is affected.

The effect is a missing peer ban, not a crash or a chain issue. Invalid blocks are still rejected. Your node continues to operate correctly; it simply fails to ban a peer that keeps supplying invalid gossiped blocks.

## Summary

A peer that supplies a consensus-invalid gossiped block should receive a misbehavior score and, at the maximum score, an IP ban. On the inbound gossip block path this ban never fires. The verifier returns a `RouterError`, but the cleanup step downcasts the boxed error to `VerifyBlockError`; that downcast always fails for production verification errors, so the score is discarded. The invalid block is still rejected, but the supplying peer is never penalized and can repeat, consuming download bandwidth, deserialization, hashing, and proof-of-work or Equihash verification on each attempt.

## Details

The inbound gossip verifier is typed on `RouterError` (`zebrad/src/components/inbound.rs:82`), wrapped in a Tower `Timeout` (`inbound.rs:279`). When the verifier rejects a block, the download stream propagates the error unchanged (`zebrad/src/components/inbound/downloads.rs:~395`). Cleanup then tests for the wrong concrete type (`inbound.rs:338`):

```rust
let Ok(err) = err.downcast::<VerifyBlockError>() else {
    continue;
};
if err.misbehavior_score() != 0 {
    let _ = misbehavior_sender.try_send((advertiser_addr, err.misbehavior_score()));
}
```

The boxed error's concrete type is `RouterError`, not `VerifyBlockError`, so the downcast fails and cleanup continues without sending the score. `RouterError::misbehavior_score()` (`zebra-consensus/src/router.rs:147`) delegates to the inner `VerifyBlockError` or `VerifyCheckpointError`, several of whose variants score the maximum 100 (invalid Equihash proof of work, invalid subsidy, bad Merkle root, difficulty failures, excessive transparent sigops, no transactions). A single 100-point update bans the IP (`zebra-network/src/address_book.rs:444`; `MAX_PEER_MISBEHAVIOR_SCORE = 100` at `constants.rs:402`).

_Trimmed to 38 lines — full report: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-8hh2-hrf2-cqf4_
