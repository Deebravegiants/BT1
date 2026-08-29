# Q3282: write-feeds via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the three `price-feeds` buffers and their order, can an unprivileged attacker make `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) leave a residue that no reconciliation pass ever inspects? `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the three `price-feeds` buffers and their order across its boundary values through `collateral-add` in simnet and assert `write-feeds` never returns a value that breaks the invariant.
