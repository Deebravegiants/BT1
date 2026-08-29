# Q5391: resolve-or-create via repay: make the per-user ledger and the vault aggregate disagree 

## Question
`resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) allocates a user id through `increment` for whatever principal the market names. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing whether the repaid asset is in the accrued debt list, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-or-create` touches, run `repay` with whether the repaid asset is in the accrued debt list, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
