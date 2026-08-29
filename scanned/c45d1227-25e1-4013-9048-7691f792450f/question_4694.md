# Q4694: total-supply-preview via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) destroy value through a truncation the opposite operation does not restore? `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the redemption receiver varied, and assert that the value `total-supply-preview` returns is identical in both runs; a divergence confirms the finding.
