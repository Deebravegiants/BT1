# Q1194: get-full-position via borrow: record a repayment larger than the value actually delivere

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) record a repayment larger than the value actually delivered? `get-full-position` returns all collateral rows regardless of the enabled bitmap, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `borrow` in simnet and assert `get-full-position` never returns a value that breaks the invariant.
