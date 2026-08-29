# Q3292: accrue-and-cache via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `accrue-and-cache` (mainnet/contracts/market/v0-4-market.clar:245) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:245` -> `accrue-and-cache`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `accrue-and-cache` keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `borrow` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
