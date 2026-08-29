# Q1826: next-index via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) record a repayment larger than the value actually delivered? `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `min-shares` (the only slippage bound on the deposit leg) varied, and assert that the value `next-index` returns is identical in both runs; a divergence confirms the finding.
