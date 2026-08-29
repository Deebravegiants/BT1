# Q4081: collateral-remove via transfer: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling `amount`, drive `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) — which decrements the map and writes the entry before `send-tokens` executes — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with `amount`, then read `collateral-remove` state before and after in the same block and assert the two sides of the invariant are equal.
