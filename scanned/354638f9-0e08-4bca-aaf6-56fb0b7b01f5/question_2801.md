# Q2801: mask-shift-combine via supply-collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling the `ft` trait principal deciding which vault is routed to, drive `mask-shift-combine` (mainnet/contracts/market/v0-4-market.clar:422) — which folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:422` -> `mask-shift-combine`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with the `ft` trait principal deciding which vault is routed to, and assert the attacker's net token balance change is zero or negative.
