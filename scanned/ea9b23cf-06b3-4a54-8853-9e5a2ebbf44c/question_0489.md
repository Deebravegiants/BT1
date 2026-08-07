# Q0489: non_circulating_accounts arithmetic overflows on reachable values (non_circulating_supply.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `non_circulating_accounts` in `runtime/src/non_circulating_supply.rs` with an account whose data length changes between the check and the use, and make the arithmetic in `non_circulating_accounts` overflow, wrap, or divide by zero, so that the invariant "All arithmetic on attacker-controlled values is checked or provably bounded." breaks and the result is Liveness / Loss of Availability?

## Target
- File/function: `runtime/src/non_circulating_supply.rs` -> `non_circulating_accounts()` (around line 82)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: an account whose data length changes between the check and the use
- Exploit idea: Supply values that make `non_circulating_accounts` overflow, so debug builds abort and release builds wrap into a nonsensical accounting value.
- Invariant to test: All arithmetic on attacker-controlled values is checked or provably bounded.
- Expected Immunefi impact: Liveness / Loss of Availability - consensus halts and requires human intervention (1,250-5,000 SOL)
- Fast validation: Proptest `non_circulating_accounts` across full integer ranges; assert checked arithmetic and no wrap in release mode.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.
