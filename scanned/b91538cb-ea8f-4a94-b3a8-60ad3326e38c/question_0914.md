# Q0914: vault-socialize-debt via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `vault-socialize-debt` (mainnet/contracts/market/v0-4-market.clar:216) mint shares whose backing was never received? `vault-socialize-debt` routes a scaled write-down to one of six vaults, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:216` -> `vault-socialize-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `vault-socialize-debt` routes a scaled write-down to one of six vaults. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `vault-socialize-debt` returns is identical in both runs; a divergence confirms the finding.
