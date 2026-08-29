# Q3042: get-cached-indexes via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the full batch list and its ordering, can an unprivileged attacker make `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) leave a residue that no reconciliation pass ever inspects? `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the full batch list and its ordering across its boundary values through `liquidate-multi` in simnet and assert `get-cached-indexes` never returns a value that breaks the invariant.
