# Q4350: is-liquidation-paused via liquidate-multi: destroy value through a truncation the opposite operation 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `is-liquidation-paused` (mainnet/contracts/market/v0-4-market.clar:691) destroy value through a truncation the opposite operation does not restore? `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:691` -> `is-liquidation-paused`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live. Reach it through `liquidate-multi` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz how many entries share one price snapshot (price-feeds is passed as none) across its boundary values through `liquidate-multi` in simnet and assert `is-liquidation-paused` never returns a value that breaks the invariant.
