# Q3216: calc-final-liquidation-amounts via liquidate: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `min-collateral-expected` reach `calc-final-liquidation-amounts` (mainnet/contracts/market/v0-4-market.clar:834) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:834` -> `calc-final-liquidation-amounts`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `calc-final-liquidation-amounts` recomputes debt proportionally when collateral was capped, a SECOND re-derivation after `process-debt-asset` already capped once. Reach it through `liquidate` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `min-collateral-expected` across its boundary values through `liquidate` in simnet and assert `calc-final-liquidation-amounts` never returns a value that breaks the invariant.
