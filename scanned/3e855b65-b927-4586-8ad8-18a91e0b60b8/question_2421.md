# Q2421: increment via collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling whether this asset is already collateral (the is-new-collateral branch), drive `increment` (mainnet/contracts/market/v0-market-vault.clar:137) — which advances the user-id nonce — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `increment` advances the user-id nonce. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `increment` touches, run `collateral-add` with whether this asset is already collateral (the is-new-collateral branch), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
