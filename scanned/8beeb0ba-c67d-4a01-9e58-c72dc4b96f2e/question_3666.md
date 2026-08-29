# Q3666: unpack-u16 via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the three `price-feeds` buffers and their order, can an unprivileged attacker make `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) leave a residue that no reconciliation pass ever inspects? `unpack-u16` unpacks eight u16 curve fields from one packed word, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the three `price-feeds` buffers and their order across its boundary values through `collateral-add` in simnet and assert `unpack-u16` never returns a value that breaks the invariant.
