# Q5897: convert-to-shares-preview via accrue: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the utilization the rate is interpolated at, drive `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) — which returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `accrue` call, then the attacker-shaped one with the utilization the rate is interpolated at, and assert the attacker's net token balance change is zero or negative.
