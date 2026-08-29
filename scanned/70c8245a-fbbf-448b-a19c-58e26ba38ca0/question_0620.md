# Q0620: interest-rate via deposit: destroy value through a truncation the opposite operation 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls whether the vault is at a zero-supply or zero-asset edge reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it interpolates the packed curve at the current utilization, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with whether the vault is at a zero-supply or zero-asset edge varied, and assert that the value `interest-rate` returns is identical in both runs; a divergence confirms the finding.
