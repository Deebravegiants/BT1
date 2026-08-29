# Q5483: process-collateral-asset via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
`process-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:789) computes expected collateral, then caps it at the borrower's balance. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the trait principals supplied per entry, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:789` -> `process-collateral-asset`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate-multi` call, then the attacker-shaped one with the trait principals supplied per entry, and assert the attacker's net token balance change is zero or negative.
