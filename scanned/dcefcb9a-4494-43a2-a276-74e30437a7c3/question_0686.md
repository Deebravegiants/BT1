# Q0686: resolve-interpolation-points via call-ststx-ratio: mint shares whose backing was never received

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling whether the ratio is fetched before or after other state changes in the block, can an unprivileged attacker make `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) mint shares whose backing was never received? `resolve-interpolation-points` selects the bracketing curve points for a utilization, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `call-ststx-ratio` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with whether the ratio is fetched before or after other state changes in the block varied, and assert that the value `resolve-interpolation-points` returns is identical in both runs; a divergence confirms the finding.
