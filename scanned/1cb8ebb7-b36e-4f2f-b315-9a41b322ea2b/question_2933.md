# Q2933: vault-system-repay via liquidate: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `borrower`, any third-party principal, drive `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) — which routes a repayment to one of six vaults by asset id — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `borrower`, any third-party principal, and assert the attacker's net token balance change is zero or negative.
