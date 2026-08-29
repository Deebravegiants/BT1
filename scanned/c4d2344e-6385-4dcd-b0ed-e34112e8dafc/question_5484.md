# Q5484: uint-to-list-u64 via collateral-add: record a repayment larger than the value actually delivere

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls whether this asset is already collateral (the is-new-collateral branch) reach `uint-to-list-u64` (mainnet/contracts/registry/v0-assets.clar:80) in a state where it record a repayment larger than the value actually delivered? Given that it expands a bitmap into a 64-element list, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:80` -> `uint-to-list-u64`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `uint-to-list-u64` expands a bitmap into a 64-element list. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether this asset is already collateral (the is-new-collateral branch) across its boundary values through `collateral-add` in simnet and assert `uint-to-list-u64` never returns a value that breaks the invariant.
