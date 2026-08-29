# Q0520: interpolate-rate via deposit: destroy value through a truncation the opposite operation 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls whether the vault is at a zero-supply or zero-asset edge reach `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it interpolates between packed u16 curve points, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `deposit` with whether the vault is at a zero-supply or zero-asset edge, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
