# Q4536: interest-rate via deposit: mint shares whose backing was never received

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls whether the vault is at a zero-supply or zero-asset edge reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it mint shares whose backing was never received? Given that it interpolates the packed curve at the current utilization, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz whether the vault is at a zero-supply or zero-asset edge across its boundary values through `deposit` in simnet and assert `interest-rate` never returns a value that breaks the invariant.
