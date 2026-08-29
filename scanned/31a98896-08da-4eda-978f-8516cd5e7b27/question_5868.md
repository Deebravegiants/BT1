# Q5868: calc-principal-ratio-reduction via accrue: record a repayment larger than the value actually delivere

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) in a state where it record a repayment larger than the value actually delivered? Given that it reduces scaled principal proportionally to an amount over total debt, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the utilization the rate is interpolated at across its boundary values through `accrue` in simnet and assert `calc-principal-ratio-reduction` never returns a value that breaks the invariant.
