# Q3402: total-debt via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling whether the vault is at a zero-supply or zero-asset edge, can an unprivileged attacker make `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) leave a residue that no reconciliation pass ever inspects? `total-debt` computes cumulative debt from `principal-scaled` and `index`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz whether the vault is at a zero-supply or zero-asset edge across its boundary values through `deposit` in simnet and assert `total-debt` never returns a value that breaks the invariant.
