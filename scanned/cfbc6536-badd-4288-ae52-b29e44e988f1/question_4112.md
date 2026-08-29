# Q4112: calc-index-next via deposit: mint shares whose backing was never received

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `amount` reach `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) in a state where it mint shares whose backing was never received? Given that it applies a multiplier to the current index, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `amount` varied, and assert that the value `calc-index-next` returns is identical in both runs; a divergence confirms the finding.
