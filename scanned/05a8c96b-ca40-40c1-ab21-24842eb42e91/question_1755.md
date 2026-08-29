# Q1755: uint-to-list-u64 via liquidate: leave a residue that no reconciliation pass ever inspects

## Question
`uint-to-list-u64` (mainnet/contracts/registry/v0-assets.clar:80) expands a bitmap into a 64-element list. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `collateral-receiver`, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:80` -> `uint-to-list-u64`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `uint-to-list-u64` expands a bitmap into a 64-element list. Reach it through `liquidate` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `uint-to-list-u64` touches, run `liquidate` with `collateral-receiver`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
