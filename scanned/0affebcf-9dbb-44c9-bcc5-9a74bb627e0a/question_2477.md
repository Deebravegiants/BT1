# Q2477: iter-find-superset via borrow: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) — which short-circuits on the first superset match — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
