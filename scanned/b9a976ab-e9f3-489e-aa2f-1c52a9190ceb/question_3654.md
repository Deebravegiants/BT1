# Q3654: write-feed via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `min-underlying`, can an unprivileged attacker make `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) leave a residue that no reconciliation pass ever inspects? `write-feed` applies one Pyth price-feed update and folds its status, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-underlying` across its boundary values through `collateral-remove-redeem` in simnet and assert `write-feed` never returns a value that breaks the invariant.
