# Q0706: convert-to-shares-preview via liquidate-redeem: mint shares whose backing was never received

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) mint shares whose backing was never received? `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the redemption receiver, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
