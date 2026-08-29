# Q1128: increment via transfer: count one deposit as backing for two simultaneous claims

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `increment` (mainnet/contracts/market/v0-market-vault.clar:137) in a state where it count one deposit as backing for two simultaneous claims? Given that it advances the user-id nonce, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `increment` advances the user-id nonce. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the destination principal, including the market, the market-vault or the treasury across its boundary values through `transfer` in simnet and assert `increment` never returns a value that breaks the invariant.
