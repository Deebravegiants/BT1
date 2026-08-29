# Q3772: linear-interpolate via liquidate-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the vault whose share price the redemption moves reach `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it interpolates between two points, dividing by `(- x2 x1)`, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `liquidate-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the vault whose share price the redemption moves, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
