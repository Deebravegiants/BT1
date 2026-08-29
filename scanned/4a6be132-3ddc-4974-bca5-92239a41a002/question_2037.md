# Q2037: population via collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling whether this asset is already collateral (the is-new-collateral branch), drive `population` (mainnet/contracts/registry/v0-egroup.clar:81) — which counts set bits to order the bucket search — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:81` -> `population`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `population` counts set bits to order the bucket search. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `population` touches, run `collateral-add` with whether this asset is already collateral (the is-new-collateral branch), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
