# Q5607: get-egroup via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
`get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `receiver`, including a contract principal, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `get-egroup` touches, run `borrow` with `receiver`, including a contract principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
