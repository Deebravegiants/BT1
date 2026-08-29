# Q1038: find via borrow: record a repayment larger than the value actually delivere

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `amount`, can an unprivileged attacker make `find` (mainnet/contracts/registry/v0-assets.clar:135) record a repayment larger than the value actually delivered? `find` resolves an asset record from a principal through the `reverse` map, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `borrow` in simnet and assert `find` never returns a value that breaks the invariant.
