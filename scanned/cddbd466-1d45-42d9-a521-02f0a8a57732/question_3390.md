# Q3390: collateral-remove via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `min-collateral-expected`, can an unprivileged attacker make `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) leave a residue that no reconciliation pass ever inspects? `collateral-remove` decrements the map and writes the entry before `send-tokens` executes, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `collateral-remove` never returns a value that breaks the invariant.
