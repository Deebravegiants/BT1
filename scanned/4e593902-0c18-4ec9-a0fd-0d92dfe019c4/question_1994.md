# Q1994: claim_payout can pay or release value before final settlement

## Question
Can an unprivileged attacker trigger `claim_payout` while the underlying position, claim, or object is not truly final and extract funds, release deposits, or erase evidence too early?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::claim_payout
- Entrypoint: signed extrinsic `claim_payout`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Race the public claim or cleanup path against the last transition that should decide eligibility.
- Invariant to test: Any payout, refund, or cleanup must require a terminal state that every related ledger agrees on.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Invoke the call at every intermediate state boundary and verify no early release occurs.
