# Q3729: resolve-interpolation-points via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling the trait principals supplied per entry, drive `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) — which selects the bracketing curve points for a utilization — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-interpolation-points` touches, run `liquidate-multi` with the trait principals supplied per entry, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
