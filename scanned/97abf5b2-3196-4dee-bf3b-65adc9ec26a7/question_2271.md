# Q2271: price-multi-resolve via borrow: destroy value through a truncation the opposite operation 

## Question
`price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the future mask produced by the new debt bit, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `price-multi-resolve` touches, run `borrow` with the future mask produced by the new debt bit, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
