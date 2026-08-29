# Q5933: find via borrow: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the future mask produced by the new debt bit, drive `find` (mainnet/contracts/registry/v0-assets.clar:135) — which resolves an asset record from a principal through the `reverse` map — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with the future mask produced by the new debt bit, and assert the attacker's net token balance change is zero or negative.
