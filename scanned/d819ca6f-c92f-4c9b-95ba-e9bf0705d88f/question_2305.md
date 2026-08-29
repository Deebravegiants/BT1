# Q2305: is-healthy via liquidate-multi: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling which borrowers are placed early versus late in the batch, drive `is-healthy` (mainnet/contracts/market/v0-4-market.clar:656) — which returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)` — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:656` -> `is-healthy`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `is-healthy` returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with which borrowers are placed early versus late in the batch, then read `is-healthy` state before and after in the same block and assert the two sides of the invariant are equal.
