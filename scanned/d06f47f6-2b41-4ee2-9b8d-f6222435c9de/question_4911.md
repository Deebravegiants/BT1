# Q4911: find-and-resolve-asset-value via collateral-remove-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
`find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `amount` used for BOTH the collateral removal and the share redemption, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `collateral-remove-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `find-and-resolve-asset-value` touches, run `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
