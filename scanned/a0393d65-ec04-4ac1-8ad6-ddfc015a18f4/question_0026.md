# Q0026: filter-out-debt-asset via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) mint shares whose backing was never received? `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `filter-out-debt-asset` returns is identical in both runs; a divergence confirms the finding.
