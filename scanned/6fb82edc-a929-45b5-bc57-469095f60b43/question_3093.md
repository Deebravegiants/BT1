# Q3093: add-user-scaled-debt via borrow: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the order of accrual versus price resolution inside the let, drive `add-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:237) — which adds to the scaled debt row with a graceful u0 default — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:237` -> `add-user-scaled-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `add-user-scaled-debt` adds to the scaled debt row with a graceful u0 default. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `add-user-scaled-debt` touches, run `borrow` with the order of accrual versus price resolution inside the let, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
