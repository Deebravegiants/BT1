# Q5748: zip via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the `ft` trait principal deciding which vault is routed to reach `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) in a state where it record a repayment larger than the value actually delivered? Given that it pairs the utilization and rate point lists element by element, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `ft` trait principal deciding which vault is routed to across its boundary values through `supply-collateral-add` in simnet and assert `zip` never returns a value that breaks the invariant.
