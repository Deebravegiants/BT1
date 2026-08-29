# Q5859: mask-to-list-iter via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
`mask-to-list-iter` (mainnet/contracts/market/v0-4-market.clar:440) appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing `amount`, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:440` -> `mask-to-list-iter`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `mask-to-list-iter` touches, run `collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
