# Q4766: vault-accrue via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the set of assets held, can an unprivileged attacker make `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) destroy value through a truncation the opposite operation does not restore? `vault-accrue` dispatches accrual to one of six vaults by asset id, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the set of assets held varied, and assert that the value `vault-accrue` returns is identical in both runs; a divergence confirms the finding.
