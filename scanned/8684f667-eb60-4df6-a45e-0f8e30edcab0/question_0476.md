# Q0476: is-healthy-with-mask via borrow: destroy value through a truncation the opposite operation 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `receiver`, including a contract principal reach `is-healthy-with-mask` (mainnet/contracts/market/v0-4-market.clar:663) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it resolves an egroup for a caller-influenced mask and applies its LTV-BORROW, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:663` -> `is-healthy-with-mask`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `receiver`, including a contract principal varied, and assert that the value `is-healthy-with-mask` returns is identical in both runs; a divergence confirms the finding.
