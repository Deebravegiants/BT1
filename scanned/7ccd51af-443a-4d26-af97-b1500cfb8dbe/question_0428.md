# Q0428: calc-cumulative-debt via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the `ft` trait principal deciding which vault is routed to reach `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it multiplies scaled principal by an index, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with the `ft` trait principal deciding which vault is routed to varied, and assert that the value `calc-cumulative-debt` returns is identical in both runs; a divergence confirms the finding.
