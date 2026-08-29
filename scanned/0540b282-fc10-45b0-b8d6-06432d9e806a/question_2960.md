# Q2960: convert-to-shares-preview via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the utilization the rate is interpolated at varied, and assert that the value `convert-to-shares-preview` returns is identical in both runs; a divergence confirms the finding.
