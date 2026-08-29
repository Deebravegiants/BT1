# Q4586: get-egroup via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) destroy value through a truncation the opposite operation does not restore? `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with the `price-feeds` buffers and their ordering varied, and assert that the value `get-egroup` returns is identical in both runs; a divergence confirms the finding.
