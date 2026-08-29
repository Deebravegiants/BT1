# Q3833: oracle-last-update via call-ststx-ratio: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), controlling whether the ratio is fetched before or after other state changes in the block, drive `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) — which returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `call-ststx-ratio` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `call-ststx-ratio` call, then the attacker-shaped one with whether the ratio is fetched before or after other state changes in the block, and assert the attacker's net token balance change is zero or negative.
