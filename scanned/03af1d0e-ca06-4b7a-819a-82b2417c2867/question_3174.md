# Q3174: calc-principal-ratio-reduction via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `min-out`, can an unprivileged attacker make `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) leave a residue that no reconciliation pass ever inspects? `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-out` across its boundary values through `deposit` in simnet and assert `calc-principal-ratio-reduction` never returns a value that breaks the invariant.
