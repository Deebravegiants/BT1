# Q1800: resolve-pyth via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) in a state where it count one deposit as backing for two simultaneous claims? Given that it reads the Pyth storage record for a 32-byte ident, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `supply-collateral-add` in simnet and assert `resolve-pyth` never returns a value that breaks the invariant.
