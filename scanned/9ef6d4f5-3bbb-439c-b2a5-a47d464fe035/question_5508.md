# Q5508: refresh via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the future mask produced by the new debt bit reach `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) in a state where it record a repayment larger than the value actually delivered? Given that it rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the future mask produced by the new debt bit across its boundary values through `borrow` in simnet and assert `refresh` never returns a value that breaks the invariant.
