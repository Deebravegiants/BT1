# Q0092: vault-system-repay via repay: destroy value through a truncation the opposite operation 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it routes a repayment to one of six vaults by asset id, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with whether the repaid asset is in the accrued debt list varied, and assert that the value `vault-system-repay` returns is identical in both runs; a divergence confirms the finding.
