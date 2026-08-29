# Q3164: get-available-assets via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the utilization the rate is interpolated at varied, and assert that the value `get-available-assets` returns is identical in both runs; a divergence confirms the finding.
