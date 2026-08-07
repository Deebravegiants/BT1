# Q0488: calculate_non_circulating_supply panics on attacker-reachable input (non_circulating_supply.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `calculate_non_circulating_supply` in `runtime/src/non_circulating_supply.rs` with a denominator that the attacker can drive to zero or one, and reach an unchecked unwrap, slice index, or assertion inside `calculate_non_circulating_supply`, so that the invariant "No attacker-reachable input causes a panic, abort, or assertion failure; failures are returned as errors." breaks and the result is Liveness / Loss of Availability?

## Target
- File/function: `runtime/src/non_circulating_supply.rs` -> `calculate_non_circulating_supply()` (around line 19)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: a denominator that the attacker can drive to zero or one
- Exploit idea: Reach `calculate_non_circulating_supply` with input that trips an unwrap, slice index, `expect`, division, or debug assertion, aborting the process on every node that replays the block.
- Invariant to test: No attacker-reachable input causes a panic, abort, or assertion failure; failures are returned as errors.
- Expected Immunefi impact: Liveness / Loss of Availability - consensus halts and requires human intervention (1,250-5,000 SOL)
- Fast validation: Fuzz `calculate_non_circulating_supply` with `cargo fuzz`/proptest over its attacker-controlled arguments; assert no panic, only `Result::Err`.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.
