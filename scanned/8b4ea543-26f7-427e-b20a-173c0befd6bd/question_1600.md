# Q1600: ubalance via transfer: count one deposit as backing for two simultaneous claims

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls `amount` reach `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) in a state where it count one deposit as backing for two simultaneous claims? Given that it reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `transfer` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
