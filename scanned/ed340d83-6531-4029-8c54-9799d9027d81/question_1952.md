# Q1952: calc-principal-ratio-reduction via accrue: count one deposit as backing for two simultaneous claims

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls whether an earlier call in the same block already advanced last-update reach `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) in a state where it count one deposit as backing for two simultaneous claims? Given that it reduces scaled principal proportionally to an amount over total debt, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with whether an earlier call in the same block already advanced last-update varied, and assert that the value `calc-principal-ratio-reduction` returns is identical in both runs; a divergence confirms the finding.
