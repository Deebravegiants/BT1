# Q1960: interest-rate via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls call ordering within the block reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it credit one side of an accounting pair without the other? Given that it interpolates the packed curve at the current utilization, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `collateral-add` with call ordering within the block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
