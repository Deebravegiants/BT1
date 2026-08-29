# Q5499: unwrap-status via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
`unwrap-status` (mainnet/contracts/registry/v0-assets.clar:111) resolves `status` with `unwrap-panic`. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `debt-amount`, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:111` -> `unwrap-status`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `unwrap-status` resolves `status` with `unwrap-panic`. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `unwrap-status` touches, run `liquidate` with `debt-amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
