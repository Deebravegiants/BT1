# Q0272: next-index via repay: destroy value through a truncation the opposite operation 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with whether the repaid asset is in the accrued debt list varied, and assert that the value `next-index` returns is identical in both runs; a divergence confirms the finding.
