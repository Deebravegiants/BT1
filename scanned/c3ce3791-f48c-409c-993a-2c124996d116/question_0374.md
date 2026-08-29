# Q0374: total-assets via redeem: mint shares whose backing was never received

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the vault's available liquidity relative to the redemption, can an unprivileged attacker make `total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) mint shares whose backing was never received? `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the vault's available liquidity relative to the redemption varied, and assert that the value `total-assets` returns is identical in both runs; a divergence confirms the finding.
