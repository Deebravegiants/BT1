# Q1765: calc-index-next via call-ststx-ratio: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), controlling whether the ratio is fetched before or after other state changes in the block, drive `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) — which applies a multiplier to the current index — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `call-ststx-ratio` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `call-ststx-ratio` with whether the ratio is fetched before or after other state changes in the block, then read `calc-index-next` state before and after in the same block and assert the two sides of the invariant are equal.
