# Q2204: convert-to-shares-preview via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `amount` used for BOTH the collateral removal and the share redemption reach `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) in a state where it credit one side of an accounting pair without the other? Given that it returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `amount` used for BOTH the collateral removal and the share redemption varied, and assert that the value `convert-to-shares-preview` returns is identical in both runs; a divergence confirms the finding.
