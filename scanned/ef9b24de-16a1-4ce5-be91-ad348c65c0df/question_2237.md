# Q2237: purge_special_columns_exact settles one authorization twice (blockstore_purge.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `purge_special_columns_exact` in `ledger/src/blockstore/blockstore_purge.rs` with an interleaving where the write lands between the read and the validation, and have `purge_special_columns_exact` apply the same authorized effect a second time, so that the invariant "One signed authorization produces exactly one state effect." breaks and the result is Loss of Funds?

## Target
- File/function: `ledger/src/blockstore/blockstore_purge.rs` -> `purge_special_columns_exact()` (around line 452)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: an interleaving where the write lands between the read and the validation
- Exploit idea: Get `purge_special_columns_exact` to apply the same logical effect twice from a single user authorization by re-entering it or replaying the surrounding flow.
- Invariant to test: One signed authorization produces exactly one state effect.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Integration test: submit the flow twice (and once re-entrantly) and assert the second application is rejected and balances moved once.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can replay or double-apply one signed transaction through durable-nonce advance, blockhash-queue aging, or status-cache dedup so a single authorization settles more than once.
