# Q0199: system-repay via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
`system-repay` (mainnet/contracts/vault/v0-vault-stx.clar:902) splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing which borrowers are placed early versus late in the batch, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:902` -> `system-repay`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with which borrowers are placed early versus late in the batch, then read `system-repay` state before and after in the same block and assert the two sides of the invariant are equal.
