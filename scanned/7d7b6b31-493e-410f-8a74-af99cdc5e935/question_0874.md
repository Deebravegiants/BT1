# Q0874: calc-utilization via redeem: mint shares whose backing was never received

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the vault's available liquidity relative to the redemption, can an unprivileged attacker make `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) mint shares whose backing was never received? `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `redeem` with the vault's available liquidity relative to the redemption, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
