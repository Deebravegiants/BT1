# Q5035: scale-debt-for-liquidation via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
`scale-debt-for-liquidation` (mainnet/contracts/market/v0-4-market.clar:858) re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing the `price-feeds` buffers and their ordering, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:858` -> `scale-debt-for-liquidation`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `scale-debt-for-liquidation` re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with the `price-feeds` buffers and their ordering, then read `scale-debt-for-liquidation` state before and after in the same block and assert the two sides of the invariant are equal.
