# Q3249: resolve-interpolation-points via borrow: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the order of accrual versus price resolution inside the let, drive `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) — which selects the bracketing curve points for a utilization — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `resolve-interpolation-points` touches, run `borrow` with the order of accrual versus price resolution inside the let, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
