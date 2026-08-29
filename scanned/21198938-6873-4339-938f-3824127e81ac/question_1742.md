# Q1742: resolve-interpolation-points via redeem: record a repayment larger than the value actually delivere

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `recipient`, can an unprivileged attacker make `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) record a repayment larger than the value actually delivered? `resolve-interpolation-points` selects the bracketing curve points for a utilization, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `recipient` varied, and assert that the value `resolve-interpolation-points` returns is identical in both runs; a divergence confirms the finding.
