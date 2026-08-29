# Q3618: interpolate-rate via accrue: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling whether an earlier call in the same block already advanced last-update, can an unprivileged attacker make `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) leave a residue that no reconciliation pass ever inspects? `interpolate-rate` interpolates between packed u16 curve points, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `accrue` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz whether an earlier call in the same block already advanced last-update across its boundary values through `accrue` in simnet and assert `interpolate-rate` never returns a value that breaks the invariant.
