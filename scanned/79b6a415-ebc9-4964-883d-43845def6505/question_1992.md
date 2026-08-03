# Q1992: chill can pay or release value before final settlement

## Question
Can an unprivileged attacker trigger `chill` while the underlying position, claim, or object is not truly final and extract funds, release deposits, or erase evidence too early?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::chill
- Entrypoint: signed extrinsic `chill`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Race the public claim or cleanup path against the last transition that should decide eligibility.
- Invariant to test: Any payout, refund, or cleanup must require a terminal state that every related ledger agrees on.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Invoke the call at every intermediate state boundary and verify no early release occurs.
