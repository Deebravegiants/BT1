# Q0314: get-liquidation-position via collateral-remove: mint shares whose backing was never received

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) mint shares whose backing was never received? `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `receiver`, including a contract principal varied, and assert that the value `get-liquidation-position` returns is identical in both runs; a divergence confirms the finding.
