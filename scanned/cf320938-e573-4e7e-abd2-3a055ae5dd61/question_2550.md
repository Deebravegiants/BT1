# Q2550: convert-to-scaled-debt via borrow: have the same quantity scaled twice by two contracts that 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) have the same quantity scaled twice by two contracts that round differently? `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `borrow` in simnet and assert `convert-to-scaled-debt` never returns a value that breaks the invariant.
