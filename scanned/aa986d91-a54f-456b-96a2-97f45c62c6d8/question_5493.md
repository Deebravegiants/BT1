# Q5493: resolve via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling `receiver`, including a contract principal, drive `resolve` (mainnet/contracts/registry/v0-egroup.clar:360) — which selects the efficiency group for a position mask — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:360` -> `resolve`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `resolve` selects the efficiency group for a position mask. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve` touches, run `collateral-remove` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
