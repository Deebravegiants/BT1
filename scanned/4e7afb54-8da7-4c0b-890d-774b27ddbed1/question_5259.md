# Q5259: oracle-price-legal via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
`oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) accepts any price strictly greater than zero, with no upper bound and no sanity band. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `receiver`, including a contract principal, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `oracle-price-legal` touches, run `borrow` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
