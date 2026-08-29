# Q3319: next-index via accrue: count one deposit as backing for two simultaneous claims

## Question
`next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Can an unprivileged caller of `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), by choosing the block time at which accrual is first triggered in a block, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with the block time at which accrual is first triggered in a block, then read `next-index` state before and after in the same block and assert the two sides of the invariant are equal.
