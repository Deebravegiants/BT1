# Q1818: collateral-add via collateral-add: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the `ft` trait principal, can an unprivileged attacker make `collateral-add` (mainnet/contracts/market/v0-market-vault.clar:374) record a repayment larger than the value actually delivered? `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:374` -> `collateral-add`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `collateral-add` in simnet and assert `collateral-add` never returns a value that breaks the invariant.
