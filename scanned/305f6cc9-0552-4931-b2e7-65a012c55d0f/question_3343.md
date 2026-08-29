# Q3343: write-feed via borrow: count one deposit as backing for two simultaneous claims

## Question
`write-feed` (mainnet/contracts/market/v0-4-market.clar:129) applies one Pyth price-feed update and folds its status. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the `price-feeds` buffers, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the `price-feeds` buffers, then read `write-feed` state before and after in the same block and assert the two sides of the invariant are equal.
