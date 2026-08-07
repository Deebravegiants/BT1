# Q2645: max_concurrent_connections authorization check bypassed (simple_qos.rs)

## Question
Can an unprivileged attacker entering through raw QUIC/UDP packets and transaction batches sent by an unstaked client to the leader's public TPU port reach `max_concurrent_connections` in `streamer/src/nonblocking/simple_qos.rs` with an account owned by a program the caller controls, with attacker-chosen data, and have the state change applied even though the authority stored in the target account never signed, so that the invariant "Every state change requires the signature of the authority stored in the account being changed." breaks and the result is Loss of Funds?

## Target
- File/function: `streamer/src/nonblocking/simple_qos.rs` -> `max_concurrent_connections()` (around line 422)
- Entrypoint: raw QUIC/UDP packets and transaction batches sent by an unstaked client to the leader's public TPU port
- Attacker controls: an account owned by a program the caller controls, with attacker-chosen data
- Exploit idea: Reach `max_concurrent_connections` on an account the attacker does not own and get the write applied anyway, because the check consumes a different value than the mutation does.
- Invariant to test: Every state change requires the signature of the authority stored in the account being changed.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Unit test in `streamer/src/nonblocking/simple_qos.rs`: build the instruction with a victim account and an attacker signer; assert the call returns an error and the victim account bytes are unchanged.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.
