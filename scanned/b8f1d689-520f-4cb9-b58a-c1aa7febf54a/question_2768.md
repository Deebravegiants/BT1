# Q2768: get-cached-indexes via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the position's existing collateral and debt composition reach `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) in a state where it credit one side of an accounting pair without the other? Given that it reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the position's existing collateral and debt composition varied, and assert that the value `get-cached-indexes` returns is identical in both runs; a divergence confirms the finding.
