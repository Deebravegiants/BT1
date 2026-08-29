# Q3789: send-tokens via collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling call ordering within the block, drive `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) — which pushes an asset to a caller-chosen recipient principal — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `send-tokens` touches, run `collateral-add` with call ordering within the block, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
