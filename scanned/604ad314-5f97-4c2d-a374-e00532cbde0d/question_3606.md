# Q3606: get-bitmap via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the three `price-feeds` buffers and their order, can an unprivileged attacker make `get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) leave a residue that no reconciliation pass ever inspects? `get-bitmap` returns the global enabled bitmap that every position read filters on, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the three `price-feeds` buffers and their order across its boundary values through `collateral-add` in simnet and assert `get-bitmap` never returns a value that breaks the invariant.
