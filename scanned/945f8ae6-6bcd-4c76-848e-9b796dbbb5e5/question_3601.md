# Q3601: checked_sub settles one authorization twice (mod.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `checked_sub` in `runtime/src/bank/builtins/core_bpf_migration/mod.rs` with a payload that satisfies the cheap precondition but not the full check, and have `checked_sub` apply the same authorized effect a second time, so that the invariant "One signed authorization produces exactly one state effect." breaks and the result is Loss of Funds?

## Target
- File/function: `runtime/src/bank/builtins/core_bpf_migration/mod.rs` -> `checked_sub()` (around line 41)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: a payload that satisfies the cheap precondition but not the full check
- Exploit idea: Get `checked_sub` to apply the same logical effect twice from a single user authorization by re-entering it or replaying the surrounding flow.
- Invariant to test: One signed authorization produces exactly one state effect.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Integration test: submit the flow twice (and once re-entrantly) and assert the second application is rejected and balances moved once.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can replay or double-apply one signed transaction through durable-nonce advance, blockhash-queue aging, or status-cache dedup so a single authorization settles more than once.
