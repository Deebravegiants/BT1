# Q1627: refund_submission_deposit can desync voting locks from effective voting power

## Question
Can an unprivileged attacker use `refund_submission_deposit` so voting power or delegation changes without the matching lock update, letting the same balance influence governance and move elsewhere?

## Target
- File/function: substrate/frame/referenda/src/lib.rs::refund_submission_deposit
- Entrypoint: signed extrinsic `refund_submission_deposit`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe interactions between vote, delegate, remove, and unlock paths and the lock ledger.
- Invariant to test: Governance voting power and the lock that secures it must rise and fall together.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Vote or delegate, then remove, unlock, proxy, or batch adjacent calls and assert no spendable governance power survives unlocked funds.
