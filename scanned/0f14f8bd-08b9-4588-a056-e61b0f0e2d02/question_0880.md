# Q0880: send-underlying via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the borrower targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
