# Q4070: interpolate-rate via collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling call ordering within the block, can an unprivileged attacker make `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) destroy value through a truncation the opposite operation does not restore? `interpolate-rate` interpolates between packed u16 curve points, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with call ordering within the block varied, and assert that the value `interpolate-rate` returns is identical in both runs; a divergence confirms the finding.
