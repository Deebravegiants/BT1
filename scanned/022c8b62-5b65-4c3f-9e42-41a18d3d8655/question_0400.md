# Q0400: set_root_signal_receiver can be driven into unbounded work (bank_forks_controller.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `set_root_signal_receiver` in `runtime/src/bank_forks_controller.rs` with a repeated operation that the code assumes happens at most once, and make `set_root_signal_receiver` iterate over an attacker-sized set far past the per-slot budget, so that the invariant "Iteration count in `set_root_signal_receiver` is bounded by a constant or by a value the transaction pays for." breaks and the result is Liveness / Loss of Availability?

## Target
- File/function: `runtime/src/bank_forks_controller.rs` -> `set_root_signal_receiver()` (around line 214)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: a repeated operation that the code assumes happens at most once
- Exploit idea: Grow the attacker-controlled collection `set_root_signal_receiver` iterates so a single transaction pins the replay thread far past the slot budget.
- Invariant to test: Iteration count in `set_root_signal_receiver` is bounded by a constant or by a value the transaction pays for.
- Expected Immunefi impact: Liveness / Loss of Availability - consensus halts and requires human intervention (1,250-5,000 SOL)
- Fast validation: Benchmark `set_root_signal_receiver` as the attacker-controlled size grows; assert runtime stays under the per-slot budget.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.
