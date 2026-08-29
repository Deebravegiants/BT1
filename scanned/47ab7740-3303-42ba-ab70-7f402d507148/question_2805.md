# Q2805: next-index via supply-collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `min-shares` (the only slippage bound on the deposit leg), drive `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) — which returns the stale `index` unchanged when the accrue pause state is set, instead of reverting — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `next-index` touches, run `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
