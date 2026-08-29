# Q1431: total-assets via deposit: leave a residue that no reconciliation pass ever inspects

## Question
`total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing `min-out`, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `total-assets` touches, run `deposit` with `min-out`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
