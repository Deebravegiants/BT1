# Q2823: convert-to-shares-preview via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
`convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing the position state the final collateral-add is validated against, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `convert-to-shares-preview` touches, run `supply-collateral-add` with the position state the final collateral-add is validated against, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
