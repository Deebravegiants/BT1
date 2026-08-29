# Q2449: debt-add-scaled via supply-collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `amount`, drive `debt-add-scaled` (mainnet/contracts/market/v0-market-vault.clar:442) — which stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:442` -> `debt-add-scaled`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `debt-add-scaled` stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with `amount`, then read `debt-add-scaled` state before and after in the same block and assert the two sides of the invariant are equal.
