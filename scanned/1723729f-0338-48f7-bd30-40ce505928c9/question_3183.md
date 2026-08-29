# Q3183: convert-to-shares-preview via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
`convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `amount` used for BOTH the collateral removal and the share redemption, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `convert-to-shares-preview` touches, run `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
