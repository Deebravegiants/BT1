# Q2258: interpolate-rate via redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the gap between the `assets` var and the real balance, can an unprivileged attacker make `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) have the same quantity scaled twice by two contracts that round differently? `interpolate-rate` interpolates between packed u16 curve points, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `interpolate-rate` returns is identical in both runs; a divergence confirms the finding.
