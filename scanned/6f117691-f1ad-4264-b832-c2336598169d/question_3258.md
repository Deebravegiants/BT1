# Q3258: send-underlying via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `amount`, can an unprivileged attacker make `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) leave a residue that no reconciliation pass ever inspects? `send-underlying` pushes the underlying under an `as-contract?` post-condition scope, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `deposit` in simnet and assert `send-underlying` never returns a value that breaks the invariant.
