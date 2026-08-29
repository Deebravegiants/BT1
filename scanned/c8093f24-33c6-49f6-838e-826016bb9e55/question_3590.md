# Q3590: create via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the `price-feeds` buffers, can an unprivileged attacker make `create` (mainnet/contracts/market/v0-market-vault.clar:150) leave a residue that no reconciliation pass ever inspects? `create` binds a principal to a fresh numeric id, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the `price-feeds` buffers varied, and assert that the value `create` returns is identical in both runs; a divergence confirms the finding.
