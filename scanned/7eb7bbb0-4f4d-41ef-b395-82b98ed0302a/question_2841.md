# Q2841: send-tokens via supply-collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling the `ft` trait principal deciding which vault is routed to, drive `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) — which pushes an asset to a caller-chosen recipient principal — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `send-tokens` touches, run `supply-collateral-add` with the `ft` trait principal deciding which vault is routed to, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
