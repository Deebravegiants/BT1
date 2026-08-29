# Q3702: write-feeds via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the `ft` trait principal, can an unprivileged attacker make `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) leave a residue that no reconciliation pass ever inspects? `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `collateral-remove` in simnet and assert `write-feeds` never returns a value that breaks the invariant.
