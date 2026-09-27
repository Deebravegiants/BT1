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

The sibling sync download path handles this correctly: it downcasts to `RouterError` (`zebrad/src/components/sync/downloads.rs:569`) and sends the score (`sync.rs:1185`). The gossip path is the only one that discards it.

Introduced with the misbehavior-ban feature (commit b4211aa1, 2025-02-15, #9201), so the gossip-path ban has never worked for router-typed errors.

## Impact

An unauthenticated peer, on a default node, can supply consensus-invalid gossiped blocks repeatedly without being banned. Each attempt is bounded (one block in transit per peer, a verify timeout, and a 16-block request cap), so this is a degradation of the anti-abuse ban control rather than a node failure. There is no crash, no chain split, no persistent halt, and no state corruption. The severity turns on whether the un-banned repetition (including across multiple source IPs) forces materially more work than the ban would otherwise cut off; that measurement is pending (see the engineer handover).

## Patches

TBD. Recommended fix shape: downcast to `RouterError` and send the score when nonzero, matching the existing sync-path handling. Non-`RouterError` errors (timeouts, transport failures) must remain unscored so honest peers are not banned.

```rust
let Ok(err) = err.downcast::<RouterError>() else {
    continue;
};
let score = err.misbehavior_score();
if score != 0 {
    let _ = misbehavior_sender.try_send((advertiser_addr, score));
}
```

## Workarounds

None that preserve normal operation. The node already rejects the invalid blocks; the only missing behavior is the ban, which operators cannot restore by configuration.

## Credit

Reported by evan-forbes, who localized the root cause and supplied a correct fix matching the sync-path handling. Found while reviewing downstream Zakura PR #460.

## References

- `zebrad/src/components/inbound.rs` (verifier type; cleanup downcast)
- `zebrad/src/components/inbound/downloads.rs` (error propagation)
- `zebra-consensus/src/router.rs` (`RouterError::misbehavior_score`)
- `zebra-network/src/address_book.rs`, `zebra-network/src/constants.rs` (ban threshold)
- `zebrad/src/components/sync/downloads.rs`, `zebrad/src/components/sync.rs` (correct sibling handling)
- CWE-253, CWE-704, CWE-693
