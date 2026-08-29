# Q4286: calc-treasury-lp-preview via transfer: destroy value through a truncation the opposite operation 

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling the timing relative to a pledge or a liquidation, can an unprivileged attacker make `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) destroy value through a truncation the opposite operation does not restore? `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `transfer` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with the timing relative to a pledge or a liquidation varied, and assert that the value `calc-treasury-lp-preview` returns is identical in both runs; a divergence confirms the finding.
