# Q5235: remove-user-scaled-debt via repay: make the per-user ledger and the vault aggregate disagree 

## Question
`remove-user-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:244) deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing whether the repaid asset is in the accrued debt list, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:244` -> `remove-user-scaled-debt`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `remove-user-scaled-debt` deletes the row only on an exact zero, otherwise leaving a residue that keeps the mask bit set. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `remove-user-scaled-debt` touches, run `repay` with whether the repaid asset is in the accrued debt list, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
