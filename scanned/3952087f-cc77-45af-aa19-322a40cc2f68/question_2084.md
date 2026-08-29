# Q2084: calc-liq-factor via liquidate: credit one side of an accounting pair without the other

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `calc-liq-factor` (mainnet/contracts/market/v0-4-market.clar:703) in a state where it credit one side of an accounting pair without the other? Given that it computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:703` -> `calc-liq-factor`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `calc-liq-factor` computes `(- ltv-curr ltv-liq-partial)` over `(- ltv-liq-full ltv-liq-partial)`, a subtraction that aborts below the partial threshold. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `collateral-receiver` varied, and assert that the value `calc-liq-factor` returns is identical in both runs; a divergence confirms the finding.
