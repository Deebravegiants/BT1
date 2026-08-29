# Q0458: active via collateral-remove: mint shares whose backing was never received

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `receiver`, including a contract principal, can an unprivileged attacker make `active` (mainnet/contracts/registry/v0-egroup.clar:238) mint shares whose backing was never received? `active` lists candidate bucket masks at or above a population, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:238` -> `active`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `active` lists candidate bucket masks at or above a population. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `receiver`, including a contract principal varied, and assert that the value `active` returns is identical in both runs; a divergence confirms the finding.
