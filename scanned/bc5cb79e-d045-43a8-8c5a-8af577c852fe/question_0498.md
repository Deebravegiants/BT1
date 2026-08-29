# Q0498: call-liquidate via liquidate-multi: mint shares whose backing was never received

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `call-liquidate` (mainnet/contracts/market/v0-4-market.clar:907) mint shares whose backing was never received? `call-liquidate` invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:907` -> `call-liquidate`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `call-liquidate` invokes `liquidate` with `none` for price-feeds, so a whole batch shares one snapshot. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz how many entries share one price snapshot (price-feeds is passed as none) across its boundary values through `liquidate-multi` in simnet and assert `call-liquidate` never returns a value that breaks the invariant.
