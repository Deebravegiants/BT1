# Q2310: receive-tokens via transfer: have the same quantity scaled twice by two contracts that 

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) have the same quantity scaled twice by two contracts that round differently? `receive-tokens` pulls an asset from a named account, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `transfer` in simnet and assert `receive-tokens` never returns a value that breaks the invariant.
