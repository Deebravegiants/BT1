# Q1604: calc-cumulative-debt via accrue: count one deposit as backing for two simultaneous claims

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls whether an earlier call in the same block already advanced last-update reach `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) in a state where it count one deposit as backing for two simultaneous claims? Given that it multiplies scaled principal by an index, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with whether an earlier call in the same block already advanced last-update varied, and assert that the value `calc-cumulative-debt` returns is identical in both runs; a divergence confirms the finding.
