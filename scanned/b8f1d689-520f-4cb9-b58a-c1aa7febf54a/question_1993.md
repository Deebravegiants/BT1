# Q1993: interest-rate via liquidate-multi: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling which borrowers are placed early versus late in the batch, drive `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) — which interpolates the packed curve at the current utilization — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with which borrowers are placed early versus late in the batch, then read `interest-rate` state before and after in the same block and assert the two sides of the invariant are equal.
