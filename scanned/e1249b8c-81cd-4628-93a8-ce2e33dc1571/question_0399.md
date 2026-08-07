# Q0399: receiver settles one authorization twice (bank_forks_controller.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `receiver` in `runtime/src/bank_forks_controller.rs` with arguments that drive the path into its error branch after side effects were applied, and have `receiver` apply the same authorized effect a second time, so that the invariant "One signed authorization produces exactly one state effect." breaks and the result is Loss of Funds?

## Target
- File/function: `runtime/src/bank_forks_controller.rs` -> `receiver()` (around line 210)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: arguments that drive the path into its error branch after side effects were applied
- Exploit idea: Get `receiver` to apply the same logical effect twice from a single user authorization by re-entering it or replaying the surrounding flow.
- Invariant to test: One signed authorization produces exactly one state effect.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Integration test: submit the flow twice (and once re-entrantly) and assert the second application is rejected and balances moved once.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can replay or double-apply one signed transaction through durable-nonce advance, blockhash-queue aging, or status-cache dedup so a single authorization settles more than once.
