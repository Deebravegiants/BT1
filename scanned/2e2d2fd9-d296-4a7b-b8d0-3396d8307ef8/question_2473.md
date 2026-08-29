# Q2473: calc-index-next via collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the three `price-feeds` buffers and their order, drive `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) — which applies a multiplier to the current index — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the three `price-feeds` buffers and their order, then read `calc-index-next` state before and after in the same block and assert the two sides of the invariant are equal.
