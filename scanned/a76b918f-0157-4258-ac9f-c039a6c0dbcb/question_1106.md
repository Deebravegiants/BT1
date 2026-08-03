# Q1106: unlock can settle before the object is truly final

## Question
Can an unprivileged attacker call `unlock` while the underlying governance object is not actually terminal and extract funds, clear storage, or unlock voting power too early?

## Target
- File/function: substrate/frame/conviction-voting/src/lib.rs::unlock
- Entrypoint: signed extrinsic `unlock`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Race public settlement or cleanup against the final state transition that should determine eligibility.
- Invariant to test: No public claim, refund, or unlock path may run before every related ledger agrees the object is final.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Invoke the call at every intermediate boundary and assert no early payout, refund, or unlock occurs.
