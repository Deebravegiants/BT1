# Q5291: relevant via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
`relevant` (mainnet/contracts/market/v0-market-vault.clar:175) drops any position row whose bit is not present in the enabled mask. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `collateral-receiver`, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `collateral-receiver`, and assert the attacker's net token balance change is zero or negative.
