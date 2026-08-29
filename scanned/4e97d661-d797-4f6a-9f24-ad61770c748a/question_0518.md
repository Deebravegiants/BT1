# Q0518: convert-to-shares-preview via transfer: mint shares whose backing was never received

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) mint shares whose backing was never received? `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `transfer` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with `amount` varied, and assert that the value `convert-to-shares-preview` returns is identical in both runs; a divergence confirms the finding.
