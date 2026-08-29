# Q0890: calc-liq-factor-bound via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `debt-amount`, can an unprivileged attacker make `calc-liq-factor-bound` (mainnet/contracts/market/v0-4-market.clar:718) mint shares whose backing was never received? `calc-liq-factor-bound` scales the penalty between a min and a max, capped at the max, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:718` -> `calc-liq-factor-bound`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `calc-liq-factor-bound` scales the penalty between a min and a max, capped at the max. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `calc-liq-factor-bound` returns is identical in both runs; a divergence confirms the finding.
