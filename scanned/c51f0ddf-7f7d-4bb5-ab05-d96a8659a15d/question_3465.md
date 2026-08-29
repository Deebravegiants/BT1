# Q3465: oracle-last-update via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling the trait principals supplied per entry, drive `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) — which returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `oracle-last-update` touches, run `liquidate-multi` with the trait principals supplied per entry, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
