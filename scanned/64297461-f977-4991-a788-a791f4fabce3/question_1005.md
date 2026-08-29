# Q1005: filter-out-debt-asset via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `collateral-receiver`, drive `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) — which rebuilds the debt list without one asset, under `as-max-len? ... u64` — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `filter-out-debt-asset` touches, run `liquidate` with `collateral-receiver`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
