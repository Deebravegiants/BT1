# Q2169: is-healthy via collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling whether this asset is already collateral (the is-new-collateral branch), drive `is-healthy` (mainnet/contracts/market/v0-4-market.clar:656) — which returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)` — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:656` -> `is-healthy`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `is-healthy` returns true whenever `debt-usd` is zero and otherwise compares the raw products `(* debt-usd BPS)` and `(* collateral-usd ltv)`. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `is-healthy` touches, run `collateral-add` with whether this asset is already collateral (the is-new-collateral branch), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
