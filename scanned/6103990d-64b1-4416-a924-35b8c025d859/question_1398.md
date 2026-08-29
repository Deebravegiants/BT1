# Q1398: get-liquidation-position via collateral-add: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the `ft` trait principal, can an unprivileged attacker make `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) record a repayment larger than the value actually delivered? `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `collateral-add` in simnet and assert `get-liquidation-position` never returns a value that breaks the invariant.
