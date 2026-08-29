# Q2656: calc-cumulative-debt via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `recipient` reach `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) in a state where it credit one side of an accounting pair without the other? Given that it multiplies scaled principal by an index, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `redeem` with `recipient`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
