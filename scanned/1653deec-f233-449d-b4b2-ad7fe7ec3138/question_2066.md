# Q2066: vault-accrue via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the `ft` trait principal deciding which vault is routed to, can an unprivileged attacker make `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) have the same quantity scaled twice by two contracts that round differently? `vault-accrue` dispatches accrual to one of six vaults by asset id, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with the `ft` trait principal deciding which vault is routed to varied, and assert that the value `vault-accrue` returns is identical in both runs; a divergence confirms the finding.
