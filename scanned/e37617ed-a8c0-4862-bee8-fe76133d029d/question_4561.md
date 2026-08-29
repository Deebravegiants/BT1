# Q4561: get-asset-value via borrow: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the future mask produced by the new debt bit, drive `get-asset-value` (mainnet/contracts/market/v0-4-market.clar:679) — which resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:679` -> `get-asset-value`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the future mask produced by the new debt bit, then read `get-asset-value` state before and after in the same block and assert the two sides of the invariant are equal.
