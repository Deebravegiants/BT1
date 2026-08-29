# Q2708: oracle-last-update via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the position's existing collateral and debt composition reach `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) in a state where it credit one side of an accounting pair without the other? Given that it returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the position's existing collateral and debt composition varied, and assert that the value `oracle-last-update` returns is identical in both runs; a divergence confirms the finding.
