# Q4771: filter-out-debt-asset via supply-collateral-add: credit one side of an accounting pair without the other

## Question
`filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) rebuilds the debt list without one asset, under `as-max-len? ... u64`. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing the position state the final collateral-add is validated against, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with the position state the final collateral-add is validated against, then read `filter-out-debt-asset` state before and after in the same block and assert the two sides of the invariant are equal.
