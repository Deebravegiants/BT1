# Q4670: resolve-ztoken via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling vault share price at the moment of the deposit leg, can an unprivileged attacker make `resolve-ztoken` (mainnet/contracts/market/v0-4-market.clar:343) destroy value through a truncation the opposite operation does not restore? `resolve-ztoken` reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:343` -> `resolve-ztoken`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `resolve-ztoken` reads `lindex` from the market's own `index-cache` via `get-cached-indexes`, not from the vault, then multiplies the price and divides by INDEX-PRECISION. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with vault share price at the moment of the deposit leg varied, and assert that the value `resolve-ztoken` returns is identical in both runs; a divergence confirms the finding.
