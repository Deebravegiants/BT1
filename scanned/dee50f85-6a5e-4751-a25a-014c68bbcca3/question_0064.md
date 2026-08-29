# Q0064: resolve-callcode via borrow: destroy value through a truncation the opposite operation 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `price-feeds` buffers reach `resolve-callcode` (mainnet/contracts/market/v0-4-market.clar:349) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:349` -> `resolve-callcode`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `resolve-callcode` chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with the `price-feeds` buffers, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
