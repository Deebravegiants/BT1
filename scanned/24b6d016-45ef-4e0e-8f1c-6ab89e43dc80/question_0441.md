# Q0441: accrue-user-debts via collateral-remove: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the `ft` trait principal, drive `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) — which folds accrual over the position's debt list only — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `accrue-user-debts` touches, run `collateral-remove` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
