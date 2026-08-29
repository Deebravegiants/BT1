# Q0468: interest-rate via accrue: destroy value through a truncation the opposite operation 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls whether an earlier call in the same block already advanced last-update reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it interpolates the packed curve at the current utilization, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz whether an earlier call in the same block already advanced last-update across its boundary values through `accrue` in simnet and assert `interest-rate` never returns a value that breaks the invariant.
