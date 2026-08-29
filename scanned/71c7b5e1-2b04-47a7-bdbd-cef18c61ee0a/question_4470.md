# Q4470: calc-final-liquidation-amounts via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `calc-final-liquidation-amounts` (mainnet/contracts/market/v0-4-market.clar:834) destroy value through a truncation the opposite operation does not restore? `calc-final-liquidation-amounts` recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:834` -> `calc-final-liquidation-amounts`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `calc-final-liquidation-amounts` recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz how many entries share one price snapshot (price-feeds is passed as none) across its boundary values through `liquidate-multi` in simnet and assert `calc-final-liquidation-amounts` never returns a value that breaks the invariant.
