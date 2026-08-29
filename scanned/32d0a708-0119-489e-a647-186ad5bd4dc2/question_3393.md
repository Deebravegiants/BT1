# Q3393: linear-interpolate via accrue: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling whether an earlier call in the same block already advanced last-update, drive `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) — which interpolates between two points, dividing by `(- x2 x1)` — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: whether an earlier call in the same block already advanced last-update
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `linear-interpolate` touches, run `accrue` with whether an earlier call in the same block already advanced last-update, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
