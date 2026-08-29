# Q4412: resolve-or-create via repay: mint shares whose backing was never received

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) in a state where it mint shares whose backing was never received? Given that it allocates a user id through `increment` for whatever principal the market names, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with whether the repaid asset is in the accrued debt list varied, and assert that the value `resolve-or-create` returns is identical in both runs; a divergence confirms the finding.
