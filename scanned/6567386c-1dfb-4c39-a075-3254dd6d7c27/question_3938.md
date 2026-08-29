# Q3938: find-and-resolve-asset-value via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) destroy value through a truncation the opposite operation does not restore? `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `min-shares` (the only slippage bound on the deposit leg) varied, and assert that the value `find-and-resolve-asset-value` returns is identical in both runs; a divergence confirms the finding.
