# Q0602: price-resolve via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `price-resolve` (mainnet/contracts/market/v0-4-market.clar:373) mint shares whose backing was never received? `price-resolve` resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:373` -> `price-resolve`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `price-resolve` resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `price-resolve` returns is identical in both runs; a divergence confirms the finding.
