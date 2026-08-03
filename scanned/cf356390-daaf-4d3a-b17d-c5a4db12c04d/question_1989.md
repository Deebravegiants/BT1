# Q1989: adjust_pool_deposit can pay or release value before final settlement

## Question
Can an unprivileged attacker trigger `adjust_pool_deposit` while the underlying position, claim, or object is not truly final and extract funds, release deposits, or erase evidence too early?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::adjust_pool_deposit
- Entrypoint: signed extrinsic `adjust_pool_deposit`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Race the public claim or cleanup path against the last transition that should decide eligibility.
- Invariant to test: Any payout, refund, or cleanup must require a terminal state that every related ledger agrees on.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Invoke the call at every intermediate state boundary and verify no early release occurs.
