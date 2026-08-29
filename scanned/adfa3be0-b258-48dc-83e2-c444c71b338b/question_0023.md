# Q0023: convert-to-shares-preview via accrue: have the same quantity scaled twice by two contracts that 

## Question
`convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the utilization the rate is interpolated at, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `accrue` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `accrue` call, then the attacker-shaped one with the utilization the rate is interpolated at, and assert the attacker's net token balance change is zero or negative.
