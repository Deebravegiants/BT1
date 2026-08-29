# Q0689: convert-to-shares-preview via deposit: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling the vault's supply and asset state at the moment of the call, drive `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) — which returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit — to credit one side of an accounting pair without the other, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: the vault's supply and asset state at the moment of the call
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `deposit` call, then the attacker-shaped one with the vault's supply and asset state at the moment of the call, and assert the attacker's net token balance change is zero or negative.
