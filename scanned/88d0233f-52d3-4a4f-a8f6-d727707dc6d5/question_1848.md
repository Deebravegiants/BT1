# Q1848: add-user-collateral via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) in a state where it count one deposit as backing for two simultaneous claims? Given that it adds to the collateral row with a graceful u0 default, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `borrow` in simnet and assert `add-user-collateral` never returns a value that breaks the invariant.
