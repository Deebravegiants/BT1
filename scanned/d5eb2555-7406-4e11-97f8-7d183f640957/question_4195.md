# Q4195: calc-final-liquidation-amounts via liquidate: credit one side of an accounting pair without the other

## Question
`calc-final-liquidation-amounts` (mainnet/contracts/market/v0-4-market.clar:834) recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing which collateral and debt asset pair is targeted, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:834` -> `calc-final-liquidation-amounts`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `calc-final-liquidation-amounts` recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with which collateral and debt asset pair is targeted, then read `calc-final-liquidation-amounts` state before and after in the same block and assert the two sides of the invariant are equal.
