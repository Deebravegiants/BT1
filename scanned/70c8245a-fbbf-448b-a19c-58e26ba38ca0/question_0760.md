# Q0760: total-debt via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it computes cumulative debt from `principal-scaled` and `index`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the borrower targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
