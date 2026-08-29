# Q2330: debt-preview via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) have the same quantity scaled twice by two contracts that round differently? `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `min-shares` (the only slippage bound on the deposit leg) varied, and assert that the value `debt-preview` returns is identical in both runs; a divergence confirms the finding.
