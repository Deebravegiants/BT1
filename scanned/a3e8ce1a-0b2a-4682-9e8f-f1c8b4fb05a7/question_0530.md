# Q0530: calc-multiplier-delta via redeem: mint shares whose backing was never received

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the gap between the `assets` var and the real balance, can an unprivileged attacker make `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) mint shares whose backing was never received? `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `calc-multiplier-delta` returns is identical in both runs; a divergence confirms the finding.
