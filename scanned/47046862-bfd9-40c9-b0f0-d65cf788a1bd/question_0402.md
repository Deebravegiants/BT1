# Q0402: next-index via deposit: mint shares whose backing was never received

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `min-out`, can an unprivileged attacker make `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) mint shares whose backing was never received? `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-out` across its boundary values through `deposit` in simnet and assert `next-index` never returns a value that breaks the invariant.
