# Q3558: ubalance via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling the timing relative to a pledge or a liquidation, can an unprivileged attacker make `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) leave a residue that no reconciliation pass ever inspects? `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the timing relative to a pledge or a liquidation across its boundary values through `transfer` in simnet and assert `ubalance` never returns a value that breaks the invariant.
