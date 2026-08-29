# Q1311: price-resolve via liquidate-multi: leave a residue that no reconciliation pass ever inspects

## Question
`price-resolve` (mainnet/contracts/market/v0-4-market.clar:373) resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater. Can an unprivileged caller of `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), by choosing the trait principals supplied per entry, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:373` -> `price-resolve`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `price-resolve` resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater. Reach it through `liquidate-multi` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `price-resolve` touches, run `liquidate-multi` with the trait principals supplied per entry, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
