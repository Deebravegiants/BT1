# Q3078: find-asset via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `amount` used for BOTH the collateral removal and the share redemption, can an unprivileged attacker make `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) leave a residue that no reconciliation pass ever inspects? `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` used for BOTH the collateral removal and the share redemption across its boundary values through `collateral-remove-redeem` in simnet and assert `find-asset` never returns a value that breaks the invariant.
