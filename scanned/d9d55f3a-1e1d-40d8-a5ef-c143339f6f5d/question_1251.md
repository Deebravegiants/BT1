# Q1251: next-index via repay: leave a residue that no reconciliation pass ever inspects

## Question
`next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing whether the repaid asset is in the accrued debt list, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `repay` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `next-index` touches, run `repay` with whether the repaid asset is in the accrued debt list, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
