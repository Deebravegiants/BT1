# Q4413: get-full-position via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the `ft` trait principal, drive `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) — which returns all collateral rows regardless of the enabled bitmap — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `get-full-position` touches, run `collateral-add` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
