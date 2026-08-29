# Q5757: subset via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling `receiver`, including a contract principal, drive `subset` (mainnet/contracts/market/v0-market-vault.clar:100) — which tests bitmask containment — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `subset` tests bitmask containment. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `subset` touches, run `collateral-remove` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
