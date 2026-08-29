# Q1854: oracle-price-legal via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) record a repayment larger than the value actually delivered? `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the vault whose share price the redemption moves across its boundary values through `liquidate-redeem` in simnet and assert `oracle-price-legal` never returns a value that breaks the invariant.
