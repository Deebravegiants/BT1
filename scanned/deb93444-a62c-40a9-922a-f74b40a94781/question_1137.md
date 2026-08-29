# Q1137: calc-liq-collateral-repay via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `collateral-receiver`, drive `calc-liq-collateral-repay` (mainnet/contracts/market/v0-4-market.clar:728) — which scales the repaid debt by `(+ BPS liq-penalty)` — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:728` -> `calc-liq-collateral-repay`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `calc-liq-collateral-repay` touches, run `liquidate` with `collateral-receiver`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
