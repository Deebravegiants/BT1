# Q1991: bond_extra_other can pay or release value before final settlement

## Question
Can an unprivileged attacker trigger `bond_extra_other` while the underlying position, claim, or object is not truly final and extract funds, release deposits, or erase evidence too early?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::bond_extra_other
- Entrypoint: signed extrinsic `bond_extra_other`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Race the public claim or cleanup path against the last transition that should decide eligibility.
- Invariant to test: Any payout, refund, or cleanup must require a terminal state that every related ledger agrees on.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Invoke the call at every intermediate state boundary and verify no early release occurs.
