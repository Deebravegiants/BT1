# Q4188: next-index via repay: mint shares whose backing was never received

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) in a state where it mint shares whose backing was never received? Given that it returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the repaid asset is in the accrued debt list across its boundary values through `repay` in simnet and assert `next-index` never returns a value that breaks the invariant.
