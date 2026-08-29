# Q0572: calc-treasury-lp-preview via accrue: destroy value through a truncation the opposite operation 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the utilization the rate is interpolated at varied, and assert that the value `calc-treasury-lp-preview` returns is identical in both runs; a divergence confirms the finding.
