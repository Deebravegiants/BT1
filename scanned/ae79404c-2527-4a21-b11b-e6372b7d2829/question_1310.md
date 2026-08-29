# Q1310: convert-to-assets-preview via redeem: record a repayment larger than the value actually delivere

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `amount` of shares burned, can an unprivileged attacker make `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) record a repayment larger than the value actually delivered? `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `amount` of shares burned varied, and assert that the value `convert-to-assets-preview` returns is identical in both runs; a divergence confirms the finding.
