# Q2777: mask-to-list-internal via borrow: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) — which expands mask bits into a list bounded at 64 entries — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
