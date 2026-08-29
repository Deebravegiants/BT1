# Q3455: convert-to-shares-preview via transfer: count one deposit as backing for two simultaneous claims

## Question
`convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing `amount`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `transfer` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `transfer` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
