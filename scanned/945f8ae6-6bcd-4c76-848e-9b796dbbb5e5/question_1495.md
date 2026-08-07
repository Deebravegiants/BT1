# Q1495: new_from_file_info_unchecked authorization check bypassed (append_vec.rs)

## Question
Can an unprivileged attacker entering through ordinary transactions that create, write, resize, close and reopen accounts the attacker pays for reach `new_from_file_info_unchecked` in `accounts-db/src/append_vec.rs` with an alternate encoding of the same logical value that the check normalizes differently, and have the state change applied even though the authority stored in the target account never signed, so that the invariant "Every state change requires the signature of the authority stored in the account being changed." breaks and the result is Loss of Funds?

## Target
- File/function: `accounts-db/src/append_vec.rs` -> `new_from_file_info_unchecked()` (around line 344)
- Entrypoint: ordinary transactions that create, write, resize, close and reopen accounts the attacker pays for
- Attacker controls: an alternate encoding of the same logical value that the check normalizes differently
- Exploit idea: Reach `new_from_file_info_unchecked` on an account the attacker does not own and get the write applied anyway, because the check consumes a different value than the mutation does.
- Invariant to test: Every state change requires the signature of the authority stored in the account being changed.
- Expected Immunefi impact: Loss of Funds - theft or creation of lamports/tokens without the owner's signature (6,250-25,000 SOL)
- Fast validation: Unit test in `accounts-db/src/append_vec.rs`: build the instruction with a victim account and an attacker signer; assert the call returns an error and the victim account bytes are unchanged.

## Bounty scope note
In-scope target per anza-xyz/agave SECURITY.md. Assumes no validator, leader,
staked-node, peer, gossip, operator, or leaked-key capability. Folder scope:
Critical. An unprivileged attacker can craft a transaction whose fee, rent, rollback, or balance-commit accounting in the SVM lifecycle moves, mints, duplicates, or destroys lamports the signer does not own.
