# Q4460: receive-underlying via redeem: mint shares whose backing was never received

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the vault's available liquidity relative to the redemption reach `receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) in a state where it mint shares whose backing was never received? Given that it pulls the underlying from a named account, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the vault's available liquidity relative to the redemption varied, and assert that the value `receive-underlying` returns is identical in both runs; a divergence confirms the finding.
