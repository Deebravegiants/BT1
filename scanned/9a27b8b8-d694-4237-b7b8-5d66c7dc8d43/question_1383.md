# Q1383: find-asset via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
`find-asset` (mainnet/contracts/market/v0-4-market.clar:584) returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `collateral-receiver`, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `find-asset` touches, run `liquidate` with `collateral-receiver`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
