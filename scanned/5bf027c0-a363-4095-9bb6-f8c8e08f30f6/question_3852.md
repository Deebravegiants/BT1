# Q3852: next-liquidity-index via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `min-collateral-expected` reach `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `next-liquidity-index` never returns a value that breaks the invariant.
