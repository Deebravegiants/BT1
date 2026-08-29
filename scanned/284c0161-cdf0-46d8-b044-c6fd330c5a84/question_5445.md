# Q5445: debt-preview via accrue: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the utilization the rate is interpolated at, drive `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) — which computes cumulative debt from `principal-scaled` and the FORWARD index — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `accrue` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `debt-preview` touches, run `accrue` with the utilization the rate is interpolated at, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
