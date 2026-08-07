# Q3346: get_non_rooted confuses account types or owners (bank_forks.rs)

## Question
Can an unprivileged attacker entering through a transaction that lands in a block and is replayed by every node on the cluster reach `get_non_rooted` in `runtime/src/bank_forks.rs` with a key that exists on an ancestor fork but not the current one, and have `get_non_rooted` deserialize an account of the wrong owner or discriminant as valid, so that the invariant "`get_non_rooted` validates owner and discriminant before trusting deserialized content." breaks and the result is Loss of Funds?

## Target
- File/function: `runtime/src/bank_forks.rs` -> `get_non_rooted()` (around line 724)
- Entrypoint: a transaction that lands in a block and is replayed by every node on the cluster
- Attacker controls: a key that exists on an ancestor fork but not the current one
- Exploit idea: Pass an account of a different type/owner that `get_non_rooted` deserializes successfully, so a later check trusts the wrong discriminant.
- Invariant to test: `get_non_rooted` validates owner and discriminant before trusting deserialized content.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Feed every other account layout into `get_non_rooted` and assert each is rejected rather than silently reinterpreted.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.
