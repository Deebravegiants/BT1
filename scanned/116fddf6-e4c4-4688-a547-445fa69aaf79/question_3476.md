# Q3476: calc-principal-ratio-reduction via redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the vault's available liquidity relative to the redemption reach `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it reduces scaled principal proportionally to an amount over total debt, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the vault's available liquidity relative to the redemption varied, and assert that the value `calc-principal-ratio-reduction` returns is identical in both runs; a divergence confirms the finding.
