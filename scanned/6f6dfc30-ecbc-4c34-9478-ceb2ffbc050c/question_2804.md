# Q2804: mask-pos via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `mask-pos` (mainnet/contracts/market/v0-market-vault.clar:91) in a state where it credit one side of an accounting pair without the other? Given that it maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:91` -> `mask-pos`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `amount` varied, and assert that the value `mask-pos` returns is identical in both runs; a divergence confirms the finding.
