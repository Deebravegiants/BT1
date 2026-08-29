# Q2497: calc-principal-ratio-reduction via redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling the vault's available liquidity relative to the redemption, drive `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) — which reduces scaled principal proportionally to an amount over total debt — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `redeem` with the vault's available liquidity relative to the redemption, then read `calc-principal-ratio-reduction` state before and after in the same block and assert the two sides of the invariant are equal.
