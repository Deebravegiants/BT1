# Q5724: mask-pos via repay: record a repayment larger than the value actually delivere

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `mask-pos` (mainnet/contracts/market/v0-market-vault.clar:91) in a state where it record a repayment larger than the value actually delivered? Given that it maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:91` -> `mask-pos`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount`, including far above the real debt (the capping path) across its boundary values through `repay` in simnet and assert `mask-pos` never returns a value that breaks the invariant.
