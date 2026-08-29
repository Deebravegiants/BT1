# Q3069: mask-update via borrow: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the order of accrual versus price resolution inside the let, drive `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) — which sets or clears one bit, clearing only when the row reaches exactly zero — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `mask-update` touches, run `borrow` with the order of accrual versus price resolution inside the let, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
