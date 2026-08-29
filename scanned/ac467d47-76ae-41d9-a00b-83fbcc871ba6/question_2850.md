# Q2850: resolve-or-create via transfer: have the same quantity scaled twice by two contracts that 

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) have the same quantity scaled twice by two contracts that round differently? `resolve-or-create` allocates a user id through `increment` for whatever principal the market names, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `transfer` in simnet and assert `resolve-or-create` never returns a value that breaks the invariant.
