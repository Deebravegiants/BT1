# Q4880: mask-to-list-iter via collateral-add: mint shares whose backing was never received

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls call ordering within the block reach `mask-to-list-iter` (mainnet/contracts/market/v0-4-market.clar:440) in a state where it mint shares whose backing was never received? Given that it appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:440` -> `mask-to-list-iter`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `mask-to-list-iter` appends under `(unwrap-panic (as-max-len? ... u64))`, aborting if the position exceeds the bound. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with call ordering within the block varied, and assert that the value `mask-to-list-iter` returns is identical in both runs; a divergence confirms the finding.
