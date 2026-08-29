# Q1359: increment via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`increment` (mainnet/contracts/market/v0-market-vault.clar:137) advances the user-id nonce. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing the position state the final collateral-add is validated against, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `increment` advances the user-id nonce. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `increment` touches, run `supply-collateral-add` with the position state the final collateral-add is validated against, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
