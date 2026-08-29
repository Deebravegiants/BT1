# Q1926: accrue-user-collateral via repay: record a repayment larger than the value actually delivere

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling the `ft` trait principal, can an unprivileged attacker make `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) record a repayment larger than the value actually delivered? `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `repay` in simnet and assert `accrue-user-collateral` never returns a value that breaks the invariant.
