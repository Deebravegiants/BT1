# Q1070: vault-system-borrow via liquidate: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `min-collateral-expected`, can an unprivileged attacker make `vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) record a repayment larger than the value actually delivered? `vault-system-borrow` routes a borrow to one of six vaults by asset id, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `min-collateral-expected` varied, and assert that the value `vault-system-borrow` returns is identical in both runs; a divergence confirms the finding.
