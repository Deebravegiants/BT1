# Q1527: receive-underlying via deposit: leave a residue that no reconciliation pass ever inspects

## Question
`receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) pulls the underlying from a named account. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing `recipient`, including a contract principal, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `receive-underlying` touches, run `deposit` with `recipient`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
