# Q5538: insert via transfer: count one deposit as backing for two simultaneous claims

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `insert` (mainnet/contracts/market/v0-market-vault.clar:159) count one deposit as backing for two simultaneous claims? `insert` rewrites the whole registry entry for a user id, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `transfer` in simnet and assert `insert` never returns a value that breaks the invariant.
