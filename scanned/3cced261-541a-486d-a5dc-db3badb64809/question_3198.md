# Q3198: get-asset-value via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `amount`, can an unprivileged attacker make `get-asset-value` (mainnet/contracts/market/v0-4-market.clar:679) leave a residue that no reconciliation pass ever inspects? `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:679` -> `get-asset-value`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `supply-collateral-add` in simnet and assert `get-asset-value` never returns a value that breaks the invariant.
