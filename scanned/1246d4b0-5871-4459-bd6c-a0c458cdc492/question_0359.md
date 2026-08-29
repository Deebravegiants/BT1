# Q0359: lookup via borrow: have the same quantity scaled twice by two contracts that 

## Question
`lookup` (mainnet/contracts/registry/v0-assets.clar:139) returns the registry record, including the `decimals` captured once at registration. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the future mask produced by the new debt bit, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with the future mask produced by the new debt bit, and assert the attacker's net token balance change is zero or negative.
