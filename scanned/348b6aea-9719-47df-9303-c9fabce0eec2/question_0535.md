# Q0535: get-available-assets via deposit: have the same quantity scaled twice by two contracts that 

## Question
`get-available-assets` (mainnet/contracts/vault/v0-vault-stx.clar:481) reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing whether the vault is at a zero-supply or zero-asset edge, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:481` -> `get-available-assets`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `get-available-assets` reads real liquidity, a different quantity from the `assets` var that `redeem` also gates on. Reach it through `deposit` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with whether the vault is at a zero-supply or zero-asset edge, then read `get-available-assets` state before and after in the same block and assert the two sides of the invariant are equal.
