# Q1576: zip via deposit: count one deposit as backing for two simultaneous claims

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `min-out` reach `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) in a state where it count one deposit as backing for two simultaneous claims? Given that it pairs the utilization and rate point lists element by element, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `deposit` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `deposit` with `min-out`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
