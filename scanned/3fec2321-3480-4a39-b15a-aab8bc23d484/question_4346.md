# Q4346: resolve-price-feed via borrow: destroy value through a truncation the opposite operation 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the order of accrual versus price resolution inside the let, can an unprivileged attacker make `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) destroy value through a truncation the opposite operation does not restore? `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the order of accrual versus price resolution inside the let varied, and assert that the value `resolve-price-feed` returns is identical in both runs; a divergence confirms the finding.
