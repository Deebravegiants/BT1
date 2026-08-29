# Q3799: subset via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
`subset` (mainnet/contracts/market/v0-market-vault.clar:100) tests bitmask containment. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing whether the position has any enabled debt row (the has-debt branch), use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `subset` tests bitmask containment. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with whether the position has any enabled debt row (the has-debt branch), then read `subset` state before and after in the same block and assert the two sides of the invariant are equal.
