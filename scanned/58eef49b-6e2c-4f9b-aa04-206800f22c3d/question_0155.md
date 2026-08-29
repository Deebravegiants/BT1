# Q0155: insert via collateral-remove-redeem: have the same quantity scaled twice by two contracts that 

## Question
`insert` (mainnet/contracts/market/v0-market-vault.clar:159) rewrites the whole registry entry for a user id. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing remaining zToken collateral whose price moves with the redeem, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `collateral-remove-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with remaining zToken collateral whose price moves with the redeem, and assert the attacker's net token balance change is zero or negative.
