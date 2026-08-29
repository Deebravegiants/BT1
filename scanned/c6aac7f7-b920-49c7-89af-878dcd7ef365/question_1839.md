# Q1839: iter-find-superset via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) short-circuits on the first superset match. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the position's existing collateral and debt composition, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `iter-find-superset` touches, run `collateral-add` with the position's existing collateral and debt composition, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
