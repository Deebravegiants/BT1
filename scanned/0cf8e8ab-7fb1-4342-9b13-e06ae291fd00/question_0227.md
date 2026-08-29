# Q0227: get-available-assets via accrue: have the same quantity scaled twice by two contracts that 

## Question
`get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the utilization the rate is interpolated at, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `accrue` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `accrue` call, then the attacker-shaped one with the utilization the rate is interpolated at, and assert the attacker's net token balance change is zero or negative.
