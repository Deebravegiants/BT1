# Q1338: lookup via borrow: record a repayment larger than the value actually delivere

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `lookup` (mainnet/contracts/registry/v0-assets.clar:139) record a repayment larger than the value actually delivered? `lookup` returns the registry record, including the `decimals` captured once at registration, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `borrow` in simnet and assert `lookup` never returns a value that breaks the invariant.
