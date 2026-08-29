# Q4819: resolve via liquidate: credit one side of an accounting pair without the other

## Question
`resolve` (mainnet/contracts/registry/v0-egroup.clar:360) selects the efficiency group for a position mask. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing which collateral and debt asset pair is targeted, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:360` -> `resolve`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `resolve` selects the efficiency group for a position mask. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with which collateral and debt asset pair is targeted, then read `resolve` state before and after in the same block and assert the two sides of the invariant are equal.
