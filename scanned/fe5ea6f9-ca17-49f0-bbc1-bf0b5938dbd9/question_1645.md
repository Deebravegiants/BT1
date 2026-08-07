# Q1645: lock_readonly can be driven into unbounded work (account_locks.rs)

## Question
Can an unprivileged attacker entering through ordinary transactions that create, write, resize, close and reopen accounts the attacker pays for reach `lock_readonly` in `accounts-db/src/account_locks.rs` with a conflict pattern that forces repeated reschedule/retry of the same transaction, and make `lock_readonly` iterate over an attacker-sized set far past the per-slot budget, so that the invariant "Iteration count in `lock_readonly` is bounded by a constant or by a value the transaction pays for." breaks and the result is Liveness / Loss of Availability?

## Target
- File/function: `accounts-db/src/account_locks.rs` -> `lock_readonly()` (around line 103)
- Entrypoint: ordinary transactions that create, write, resize, close and reopen accounts the attacker pays for
- Attacker controls: a conflict pattern that forces repeated reschedule/retry of the same transaction
- Exploit idea: Grow the attacker-controlled collection `lock_readonly` iterates so a single transaction pins the replay thread far past the slot budget.
- Invariant to test: Iteration count in `lock_readonly` is bounded by a constant or by a value the transaction pays for.
- Expected Immunefi impact: Liveness / Loss of Availability - consensus halts and requires human intervention (1,250-5,000 SOL)
- Fast validation: Benchmark `lock_readonly` as the attacker-controlled size grows; assert runtime stays under the per-slot budget.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can send a valid-looking transaction that panics, overflows, aborts, or wedges banking/replay on every node, halting consensus until human intervention.
