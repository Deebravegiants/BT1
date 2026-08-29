# Q0836: interest-rate via redeem: destroy value through a truncation the opposite operation 

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `amount` of shares burned reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it interpolates the packed curve at the current utilization, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `amount` of shares burned varied, and assert that the value `interest-rate` returns is identical in both runs; a divergence confirms the finding.
