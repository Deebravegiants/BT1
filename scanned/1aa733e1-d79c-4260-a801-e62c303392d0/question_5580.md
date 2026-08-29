# Q5580: unpack-u16 via repay: record a repayment larger than the value actually delivere

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it record a repayment larger than the value actually delivered? Given that it unpacks eight u16 curve fields from one packed word, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount`, including far above the real debt (the capping path) across its boundary values through `repay` in simnet and assert `unpack-u16` never returns a value that breaks the invariant.
