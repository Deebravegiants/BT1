# Q5811: remove-user-collateral via collateral-remove-redeem: make the per-user ledger and the vault aggregate disagree 

## Question
`remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) asserts sufficiency then `map-delete`s only on an exact zero. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `amount` used for BOTH the collateral removal and the share redemption, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `collateral-remove-redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `remove-user-collateral` touches, run `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
