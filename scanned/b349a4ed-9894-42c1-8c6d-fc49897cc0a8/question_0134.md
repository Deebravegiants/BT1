# Q0134: linear-interpolate via deposit: mint shares whose backing was never received

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling the vault's supply and asset state at the moment of the call, can an unprivileged attacker make `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) mint shares whose backing was never received? `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with the vault's supply and asset state at the moment of the call varied, and assert that the value `linear-interpolate` returns is identical in both runs; a divergence confirms the finding.
