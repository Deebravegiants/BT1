# Q1004: get-available-assets via redeem: count one deposit as backing for two simultaneous claims

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the gap between the `assets` var and the real balance reach `get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) in a state where it count one deposit as backing for two simultaneous claims? Given that it reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `get-available-assets` returns is identical in both runs; a divergence confirms the finding.
