# Q1872: send-underlying via transfer: count one deposit as backing for two simultaneous claims

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it count one deposit as backing for two simultaneous claims? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the destination principal, including the market, the market-vault or the treasury across its boundary values through `transfer` in simnet and assert `send-underlying` never returns a value that breaks the invariant.
