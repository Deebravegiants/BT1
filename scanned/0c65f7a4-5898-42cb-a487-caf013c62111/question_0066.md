# Q0066: claim_swap can break PendingSwaps / hashlock state conservation

## Question
Can an unprivileged attacker call `claim_swap` with crafted proof or signed payload contents, duplicate or adversarial list ordering so `PendingSwaps` and `hashlock state` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/atomic-swap/src/lib.rs::claim_swap
- Entrypoint: signed extrinsic `claim_swap`
- Attacker controls: proof or signed payload contents, duplicate or adversarial list ordering
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `PendingSwaps`, `hashlock state`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
