# Q1753: debt-add-scaled via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling `receiver`, including a contract principal, drive `debt-add-scaled` (mainnet/contracts/market/v0-market-vault.clar:442) — which stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:442` -> `debt-add-scaled`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `debt-add-scaled` stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with `receiver`, including a contract principal, then read `debt-add-scaled` state before and after in the same block and assert the two sides of the invariant are equal.
