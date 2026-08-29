# Q1830: collateral-remove via collateral-remove: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `amount` relative to the current collateral row (the removing-all branch), can an unprivileged attacker make `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) record a repayment larger than the value actually delivered? `collateral-remove` decrements the map and writes the entry before `send-tokens` executes, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` relative to the current collateral row (the removing-all branch) across its boundary values through `collateral-remove` in simnet and assert `collateral-remove` never returns a value that breaks the invariant.
