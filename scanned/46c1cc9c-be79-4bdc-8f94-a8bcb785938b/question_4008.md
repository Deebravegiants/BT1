# Q4008: vault-system-repay via repay: mint shares whose backing was never received

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) in a state where it mint shares whose backing was never received? Given that it routes a repayment to one of six vaults by asset id, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the repaid asset is in the accrued debt list across its boundary values through `repay` in simnet and assert `vault-system-repay` never returns a value that breaks the invariant.
