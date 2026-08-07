# Q3870: is_nonoverlapping panics on attacker-reachable input (mem_ops.rs)

## Question
Can an unprivileged attacker entering through deploying an attacker-authored sBPF program and invoking it with crafted instruction data and account lists reach `is_nonoverlapping` in `syscalls/src/mem_ops.rs` with arguments that drive the path into its error branch after side effects were applied, and reach an unchecked unwrap, slice index, or assertion inside `is_nonoverlapping`, so that the invariant "No attacker-reachable input causes a panic, abort, or assertion failure; failures are returned as errors." breaks and the result is Liveness / Loss of Availability?

## Target
- File/function: `syscalls/src/mem_ops.rs` -> `is_nonoverlapping()` (around line 13)
- Entrypoint: deploying an attacker-authored sBPF program and invoking it with crafted instruction data and account lists
- Attacker controls: arguments that drive the path into its error branch after side effects were applied
- Exploit idea: Reach `is_nonoverlapping` with input that trips an unwrap, slice index, `expect`, division, or debug assertion, aborting the process on every node that replays the block.
- Invariant to test: No attacker-reachable input causes a panic, abort, or assertion failure; failures are returned as errors.
- Expected Immunefi impact: Liveness / Loss of Availability - consensus halts and requires human intervention (1,250-5,000 SOL)
- Fast validation: Fuzz `is_nonoverlapping` with `cargo fuzz`/proptest over its attacker-controlled arguments; assert no panic, only `Result::Err`.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.
