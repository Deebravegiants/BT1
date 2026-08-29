# Q0722: get-liquidation-position via liquidate-multi: mint shares whose backing was never received

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) mint shares whose backing was never received? `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with how many entries share one price snapshot (price-feeds is passed as none) varied, and assert that the value `get-liquidation-position` returns is identical in both runs; a divergence confirms the finding.
