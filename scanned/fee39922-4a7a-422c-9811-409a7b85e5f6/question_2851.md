# Q2851: get_account_from_overwrites_or_bank authorization check bypassed (account_resolver.rs)

## Question
Can an unprivileged attacker entering through one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2 reach `get_account_from_overwrites_or_bank` in `rpc/src/rpc/account_resolver.rs` with a zero-lamport or exactly-rent-exempt-minus-one account, and have the state change applied even though the authority stored in the target account never signed, so that the invariant "Every state change requires the signature of the authority stored in the account being changed." breaks and the result is Loss of Funds?

## Target
- File/function: `rpc/src/rpc/account_resolver.rs` -> `get_account_from_overwrites_or_bank()` (around line 6)
- Entrypoint: one JSON-RPC call or websocket subscription from a single client, at most once per CLUSTER_SLOT_TIME_TARGET/2
- Attacker controls: a zero-lamport or exactly-rent-exempt-minus-one account
- Exploit idea: Reach `get_account_from_overwrites_or_bank` on an account the attacker does not own and get the write applied anyway, because the check consumes a different value than the mutation does.
- Invariant to test: Every state change requires the signature of the authority stored in the account being changed.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Unit test in `rpc/src/rpc/account_resolver.rs`: build the instruction with a victim account and an attacker signer; assert the call returns an error and the victim account bytes are unchanged.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.
