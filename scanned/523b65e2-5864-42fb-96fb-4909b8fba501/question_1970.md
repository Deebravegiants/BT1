# Q1970: linear-interpolate via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) have the same quantity scaled twice by two contracts that round differently? `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `collateral-receiver` varied, and assert that the value `linear-interpolate` returns is identical in both runs; a divergence confirms the finding.
