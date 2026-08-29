# Q1976: collateral-add via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the `ft` trait principal deciding which vault is routed to reach `collateral-add` (mainnet/contracts/market/v0-market-vault.clar:374) in a state where it credit one side of an accounting pair without the other? Given that it evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:374` -> `collateral-add`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with the `ft` trait principal deciding which vault is routed to varied, and assert that the value `collateral-add` returns is identical in both runs; a divergence confirms the finding.
