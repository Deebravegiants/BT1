# Q1309: oracle-price-legal via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling the position state the final collateral-add is validated against, drive `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) — which accepts any price strictly greater than zero, with no upper bound and no sanity band — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with the position state the final collateral-add is validated against, then read `oracle-price-legal` state before and after in the same block and assert the two sides of the invariant are equal.
