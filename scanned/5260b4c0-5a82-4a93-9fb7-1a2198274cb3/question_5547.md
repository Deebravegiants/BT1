# Q5547: is-healthy-with-mask via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
`is-healthy-with-mask` (mainnet/contracts/market/v0-4-market.clar:663) resolves an egroup for a caller-influenced mask and applies its LTV-BORROW. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing `receiver`, including a contract principal, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:663` -> `is-healthy-with-mask`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `is-healthy-with-mask` touches, run `collateral-remove` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
