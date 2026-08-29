# Q2087: population via liquidate: destroy value through a truncation the opposite operation 

## Question
`population` (mainnet/contracts/registry/v0-egroup.clar:81) counts set bits to order the bucket search. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `borrower`, any third-party principal, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:81` -> `population`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `population` counts set bits to order the bucket search. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `borrower`, any third-party principal, and assert the attacker's net token balance change is zero or negative.
