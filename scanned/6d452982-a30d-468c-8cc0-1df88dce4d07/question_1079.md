# Q1079: mask-to-list-internal via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) expands mask bits into a list bounded at 64 entries. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing call ordering within the block, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with call ordering within the block, and assert the attacker's net token balance change is zero or negative.
