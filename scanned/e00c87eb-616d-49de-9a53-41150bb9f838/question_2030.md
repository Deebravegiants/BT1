# Q2030: get-egroup via repay: have the same quantity scaled twice by two contracts that 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling whether the repaid asset is in the accrued debt list, can an unprivileged attacker make `get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) have the same quantity scaled twice by two contracts that round differently? `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `repay` twice with whether the repaid asset is in the accrued debt list varied, and assert that the value `get-egroup` returns is identical in both runs; a divergence confirms the finding.
