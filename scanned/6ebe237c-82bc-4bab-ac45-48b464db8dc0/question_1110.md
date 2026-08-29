# Q1110: relevant via repay: record a repayment larger than the value actually delivere

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling the `ft` trait principal, can an unprivileged attacker make `relevant` (mainnet/contracts/market/v0-market-vault.clar:175) record a repayment larger than the value actually delivered? `relevant` drops any position row whose bit is not present in the enabled mask, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `repay` in simnet and assert `relevant` never returns a value that breaks the invariant.
