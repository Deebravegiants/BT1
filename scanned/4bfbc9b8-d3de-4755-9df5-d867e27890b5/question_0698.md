# Q0698: calc-cumulative-debt via redeem: mint shares whose backing was never received

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `recipient`, can an unprivileged attacker make `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) mint shares whose backing was never received? `calc-cumulative-debt` multiplies scaled principal by an index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with `recipient` varied, and assert that the value `calc-cumulative-debt` returns is identical in both runs; a divergence confirms the finding.
