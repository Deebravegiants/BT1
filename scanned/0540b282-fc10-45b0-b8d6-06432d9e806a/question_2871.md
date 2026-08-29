# Q2871: total-assets-preview via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
`total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) re-derives a FORWARD index inside calls that have already accrued. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `receiver` for the underlying leg, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `total-assets-preview` touches, run `collateral-remove-redeem` with `receiver` for the underlying leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
