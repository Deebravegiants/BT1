# Q2699: subset via liquidate: destroy value through a truncation the opposite operation 

## Question
`subset` (mainnet/contracts/market/v0-market-vault.clar:100) tests bitmask containment. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `borrower`, any third-party principal, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `subset` tests bitmask containment. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `borrower`, any third-party principal, and assert the attacker's net token balance change is zero or negative.
