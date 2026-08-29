# Q4668: get-available-assets via liquidate-redeem: mint shares whose backing was never received

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the borrower targeted reach `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) in a state where it mint shares whose backing was never received? Given that it reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the borrower targeted across its boundary values through `liquidate-redeem` in simnet and assert `get-available-assets` never returns a value that breaks the invariant.
