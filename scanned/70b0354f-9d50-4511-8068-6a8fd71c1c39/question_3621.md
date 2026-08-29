# Q3621: mask-to-list-iter via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling the zToken/underlying id mapping reached (the u100 sentinel branch), drive `mask-to-list-iter` (mainnet/contracts/market/v0-4-market.clar:440) — which appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:440` -> `mask-to-list-iter`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `mask-to-list-iter` touches, run `collateral-remove-redeem` with the zToken/underlying id mapping reached (the u100 sentinel branch), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
