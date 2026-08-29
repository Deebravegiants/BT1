# Q3846: process-debt-asset via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the full batch list and its ordering, can an unprivileged attacker make `process-debt-asset` (mainnet/contracts/market/v0-4-market.clar:761) leave a residue that no reconciliation pass ever inspects? `process-debt-asset` caps debt at the max liquidatable USD and converts back to tokens with `mul-div-down`, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:761` -> `process-debt-asset`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `process-debt-asset` caps debt at the max liquidatable USD and converts back to tokens with `mul-div-down`. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the full batch list and its ordering across its boundary values through `liquidate-multi` in simnet and assert `process-debt-asset` never returns a value that breaks the invariant.
