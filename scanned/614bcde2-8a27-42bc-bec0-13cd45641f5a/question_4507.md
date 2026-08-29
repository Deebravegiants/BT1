# Q4507: active via liquidate: credit one side of an accounting pair without the other

## Question
`active` (mainnet/contracts/registry/v0-egroup.clar:238) lists candidate bucket masks at or above a population. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing which collateral and debt asset pair is targeted, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:238` -> `active`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `active` lists candidate bucket masks at or above a population. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with which collateral and debt asset pair is targeted, then read `active` state before and after in the same block and assert the two sides of the invariant are equal.
