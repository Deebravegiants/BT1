# Q1581: price-resolve via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `collateral-receiver`, drive `price-resolve` (mainnet/contracts/market/v0-4-market.clar:373) — which resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:373` -> `price-resolve`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `price-resolve` resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `price-resolve` touches, run `liquidate` with `collateral-receiver`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
