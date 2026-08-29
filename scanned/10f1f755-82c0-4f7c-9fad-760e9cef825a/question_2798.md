# Q2798: resolve-ztoken via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the trait principals supplied per entry, can an unprivileged attacker make `resolve-ztoken` (mainnet/contracts/market/v0-4-market.clar:343) have the same quantity scaled twice by two contracts that round differently? `resolve-ztoken` reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:343` -> `resolve-ztoken`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `resolve-ztoken` reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the trait principals supplied per entry varied, and assert that the value `resolve-ztoken` returns is identical in both runs; a divergence confirms the finding.
