# Q1308: accrue-and-cache via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the `ft` trait principal reach `accrue-and-cache` (mainnet/contracts/market/v0-4-market.clar:245) in a state where it count one deposit as backing for two simultaneous claims? Given that it keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:245` -> `accrue-and-cache`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `accrue-and-cache` keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `collateral-add` in simnet and assert `accrue-and-cache` never returns a value that breaks the invariant.
