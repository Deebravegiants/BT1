# Q5217: oracle-price-legal via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling `receiver`, including a contract principal, drive `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) — which accepts any price strictly greater than zero, with no upper bound and no sanity band — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `oracle-price-legal` touches, run `collateral-remove` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
