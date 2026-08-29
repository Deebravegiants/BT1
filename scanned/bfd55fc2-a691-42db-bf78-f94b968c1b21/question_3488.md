# Q3488: ubalance via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the utilization the rate is interpolated at varied, and assert that the value `ubalance` returns is identical in both runs; a divergence confirms the finding.
