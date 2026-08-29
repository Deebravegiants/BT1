# Q5196: debt-add-scaled via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `debt-add-scaled` (mainnet/contracts/market/v0-market-vault.clar:442) in a state where it record a repayment larger than the value actually delivered? Given that it stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:442` -> `debt-add-scaled`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `debt-add-scaled` stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the full batch list and its ordering across its boundary values through `liquidate-multi` in simnet and assert `debt-add-scaled` never returns a value that breaks the invariant.
