# Q3960: debt-remove-scaled via repay: mint shares whose backing was never received

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) in a state where it mint shares whose backing was never received? Given that it clears the debt bit only when the remaining scaled debt is exactly zero, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz whether the repaid asset is in the accrued debt list across its boundary values through `repay` in simnet and assert `debt-remove-scaled` never returns a value that breaks the invariant.
