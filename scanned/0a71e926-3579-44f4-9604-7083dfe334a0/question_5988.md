# Q5988: calc-utilization via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls how many entries share one price snapshot (price-feeds is passed as none) reach `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it divides debt by available liquidity, which can exceed BPS when debt outruns assets, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz how many entries share one price snapshot (price-feeds is passed as none) across its boundary values through `liquidate-multi` in simnet and assert `calc-utilization` never returns a value that breaks the invariant.
