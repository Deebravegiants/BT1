# Q3117: filter-u128 via collateral-remove: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the set of assets held, drive `filter-u128` (mainnet/contracts/registry/v0-egroup.clar:97) — which filters a 128-entry bucket list — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:97` -> `filter-u128`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `filter-u128` filters a 128-entry bucket list. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `filter-u128` touches, run `collateral-remove` with the set of assets held, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
