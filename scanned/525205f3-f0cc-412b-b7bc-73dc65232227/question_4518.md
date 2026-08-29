# Q4518: price-resolve via liquidate: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `price-resolve` (mainnet/contracts/market/v0-4-market.clar:373) destroy value through a truncation the opposite operation does not restore? `price-resolve` resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:373` -> `price-resolve`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `price-resolve` resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `price-resolve` never returns a value that breaks the invariant.
