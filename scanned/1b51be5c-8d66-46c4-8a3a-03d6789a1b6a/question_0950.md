# Q0950: vault-accrue via accrue: mint shares whose backing was never received

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the utilization the rate is interpolated at, can an unprivileged attacker make `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) mint shares whose backing was never received? `vault-accrue` dispatches accrual to one of six vaults by asset id, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the utilization the rate is interpolated at varied, and assert that the value `vault-accrue` returns is identical in both runs; a divergence confirms the finding.
