# Q1368: add-user-collateral via transfer: count one deposit as backing for two simultaneous claims

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) in a state where it count one deposit as backing for two simultaneous claims? Given that it adds to the collateral row with a graceful u0 default, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the destination principal, including the market, the market-vault or the treasury across its boundary values through `transfer` in simnet and assert `add-user-collateral` never returns a value that breaks the invariant.
