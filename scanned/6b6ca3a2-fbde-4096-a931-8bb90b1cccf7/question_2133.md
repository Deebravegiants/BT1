# Q2133: mask-to-list-collateral via liquidate: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling which collateral and debt asset pair is targeted, drive `mask-to-list-collateral` (mainnet/contracts/market/v0-4-market.clar:449) — which expands a mask to a list of ids over ITER-UINT-64 — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:449` -> `mask-to-list-collateral`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `mask-to-list-collateral` expands a mask to a list of ids over ITER-UINT-64. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `mask-to-list-collateral` touches, run `liquidate` with which collateral and debt asset pair is targeted, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
