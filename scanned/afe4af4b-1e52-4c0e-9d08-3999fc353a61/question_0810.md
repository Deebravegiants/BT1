# Q0810: migrate_legacy_hardlinks arithmetic overflows on reachable values (snapshot_utils.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `migrate_legacy_hardlinks` in `runtime/src/snapshot_utils.rs` with a request that stays one unit under the limit but repeats within a single transaction, and make the arithmetic in `migrate_legacy_hardlinks` overflow, wrap, or divide by zero, so that the invariant "All arithmetic on attacker-controlled values is checked or provably bounded." breaks and the result is Liveness / Loss of Availability?

## Target
- File/function: `runtime/src/snapshot_utils.rs` -> `migrate_legacy_hardlinks()` (around line 1338)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: a request that stays one unit under the limit but repeats within a single transaction
- Exploit idea: Supply values that make `migrate_legacy_hardlinks` overflow, so debug builds abort and release builds wrap into a nonsensical accounting value.
- Invariant to test: All arithmetic on attacker-controlled values is checked or provably bounded.
- Expected Immunefi impact: Liveness / Loss of Availability - consensus halts and requires human intervention (1,250-5,000 SOL)
- Fast validation: Proptest `migrate_legacy_hardlinks` across full integer ranges; assert checked arithmetic and no wrap in release mode.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.
