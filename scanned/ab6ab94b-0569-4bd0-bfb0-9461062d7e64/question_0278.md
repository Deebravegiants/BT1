# Q0278: interest-rate via call-ststx-ratio: mint shares whose backing was never received

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling whether the ratio is fetched before or after other state changes in the block, can an unprivileged attacker make `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) mint shares whose backing was never received? `interest-rate` interpolates the packed curve at the current utilization, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `call-ststx-ratio` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with whether the ratio is fetched before or after other state changes in the block varied, and assert that the value `interest-rate` returns is identical in both runs; a divergence confirms the finding.
