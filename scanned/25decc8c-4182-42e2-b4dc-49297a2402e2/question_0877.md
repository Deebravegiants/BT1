# Q0877: filter-u128 via liquidate: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `borrower`, any third-party principal, drive `filter-u128` (mainnet/contracts/registry/v0-egroup.clar:97) — which filters a 128-entry bucket list — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:97` -> `filter-u128`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `filter-u128` filters a 128-entry bucket list. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `borrower`, any third-party principal, then read `filter-u128` state before and after in the same block and assert the two sides of the invariant are equal.
