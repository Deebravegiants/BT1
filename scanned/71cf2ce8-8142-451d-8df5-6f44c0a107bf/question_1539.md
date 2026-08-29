# Q1539: zip via borrow: leave a residue that no reconciliation pass ever inspects

## Question
`zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) pairs the utilization and rate point lists element by element. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the `price-feeds` buffers, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `zip` touches, run `borrow` with the `price-feeds` buffers, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
