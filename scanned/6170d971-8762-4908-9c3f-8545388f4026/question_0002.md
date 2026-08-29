# Q0002: interest-rate via collateral-add: mint shares whose backing was never received

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling `amount`, can an unprivileged attacker make `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) mint shares whose backing was never received? `interest-rate` interpolates the packed curve at the current utilization, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with `amount` varied, and assert that the value `interest-rate` returns is identical in both runs; a divergence confirms the finding.
