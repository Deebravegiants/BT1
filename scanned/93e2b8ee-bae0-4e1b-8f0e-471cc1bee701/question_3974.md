# Q3974: add-user-collateral via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) destroy value through a truncation the opposite operation does not restore? `add-user-collateral` adds to the collateral row with a graceful u0 default, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with the `price-feeds` buffers and their ordering varied, and assert that the value `add-user-collateral` returns is identical in both runs; a divergence confirms the finding.
