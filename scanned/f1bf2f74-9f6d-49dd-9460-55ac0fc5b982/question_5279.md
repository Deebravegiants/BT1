# Q5279: process-collateral-asset via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
`process-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:789) computes expected collateral, then caps it at the borrower's balance. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `collateral-receiver`, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:789` -> `process-collateral-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `collateral-receiver`, and assert the attacker's net token balance change is zero or negative.
