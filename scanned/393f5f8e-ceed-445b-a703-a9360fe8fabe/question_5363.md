# Q5363: interest-rate via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
`interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) interpolates the packed curve at the current utilization. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the block time at which accrual is first triggered in a block, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `accrue` call, then the attacker-shaped one with the block time at which accrual is first triggered in a block, and assert the attacker's net token balance change is zero or negative.
