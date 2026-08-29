# Q5305: get-bitmap via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the set of assets held, drive `get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) — which returns the global enabled bitmap that every position read filters on — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with the set of assets held, then read `get-bitmap` state before and after in the same block and assert the two sides of the invariant are equal.
