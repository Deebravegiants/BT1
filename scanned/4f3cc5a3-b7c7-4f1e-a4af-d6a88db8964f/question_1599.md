# Q1599: interest-rate via deposit: leave a residue that no reconciliation pass ever inspects

## Question
`interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) interpolates the packed curve at the current utilization. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing whether the vault is at a zero-supply or zero-asset edge, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `interest-rate` touches, run `deposit` with whether the vault is at a zero-supply or zero-asset edge, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
