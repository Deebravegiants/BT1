# Q3998: find via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `find` (mainnet/contracts/registry/v0-assets.clar:135) destroy value through a truncation the opposite operation does not restore? `find` resolves an asset record from a principal through the `reverse` map, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with the `price-feeds` buffers and their ordering varied, and assert that the value `find` returns is identical in both runs; a divergence confirms the finding.
