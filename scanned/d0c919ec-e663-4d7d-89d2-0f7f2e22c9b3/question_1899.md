# Q1899: unpack-u16 via call-ststx-ratio: leave a residue that no reconciliation pass ever inspects

## Question
`unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) unpacks eight u16 curve fields from one packed word. Can an unprivileged caller of `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), by choosing whether the ratio is fetched before or after other state changes in the block, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `call-ststx-ratio` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `unpack-u16` touches, run `call-ststx-ratio` with whether the ratio is fetched before or after other state changes in the block, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
