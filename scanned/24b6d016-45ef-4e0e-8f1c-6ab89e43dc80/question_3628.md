# Q3628: next-liquidity-index via repay: make the per-user ledger and the vault aggregate disagree 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls the `ft` trait principal reach `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `repay` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
