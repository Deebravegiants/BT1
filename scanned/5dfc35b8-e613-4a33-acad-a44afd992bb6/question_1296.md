# Q1296: total-debt via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `min-underlying` reach `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) in a state where it count one deposit as backing for two simultaneous claims? Given that it computes cumulative debt from `principal-scaled` and `index`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-underlying` across its boundary values through `collateral-remove-redeem` in simnet and assert `total-debt` never returns a value that breaks the invariant.
