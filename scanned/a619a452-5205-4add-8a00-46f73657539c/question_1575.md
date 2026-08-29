# Q1575: receive-tokens via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`receive-tokens` (mainnet/contracts/market/v0-market-vault.clar:256) pulls an asset from a named account. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the position's existing collateral and debt composition, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:256` -> `receive-tokens`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `receive-tokens` pulls an asset from a named account. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `receive-tokens` touches, run `collateral-add` with the position's existing collateral and debt composition, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
