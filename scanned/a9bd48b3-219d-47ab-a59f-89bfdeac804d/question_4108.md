# Q4108: zip via liquidate-redeem: mint shares whose backing was never received

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) in a state where it mint shares whose backing was never received? Given that it pairs the utilization and rate point lists element by element, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the borrower targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
