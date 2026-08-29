# Q4046: calc-index-next via redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the gap between the `assets` var and the real balance, can an unprivileged attacker make `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) destroy value through a truncation the opposite operation does not restore? `calc-index-next` applies a multiplier to the current index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `calc-index-next` returns is identical in both runs; a divergence confirms the finding.
