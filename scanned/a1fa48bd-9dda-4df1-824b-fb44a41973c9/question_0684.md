# Q0684: mask-to-list-iter via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls the zToken/underlying id mapping reached (the u100 sentinel branch) reach `mask-to-list-iter` (mainnet/contracts/market/v0-4-market.clar:440) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:440` -> `mask-to-list-iter`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the zToken/underlying id mapping reached (the u100 sentinel branch) across its boundary values through `collateral-remove-redeem` in simnet and assert `mask-to-list-iter` never returns a value that breaks the invariant.
