# Q1470: debt-add-scaled via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `amount`, can an unprivileged attacker make `debt-add-scaled` (mainnet/contracts/market/v0-market-vault.clar:442) record a repayment larger than the value actually delivered? `debt-add-scaled` stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:442` -> `debt-add-scaled`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `debt-add-scaled` stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `supply-collateral-add` in simnet and assert `debt-add-scaled` never returns a value that breaks the invariant.
