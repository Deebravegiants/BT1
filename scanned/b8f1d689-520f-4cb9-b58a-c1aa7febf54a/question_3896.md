# Q3896: accrue-user-collateral via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it accrues only rows that `is-ztoken` recognises, skipping everything else, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the utilization the rate is interpolated at varied, and assert that the value `accrue-user-collateral` returns is identical in both runs; a divergence confirms the finding.
