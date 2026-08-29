# Q4622: convert-to-shares-preview via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) destroy value through a truncation the opposite operation does not restore? `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the redemption receiver varied, and assert that the value `convert-to-shares-preview` returns is identical in both runs; a divergence confirms the finding.
