# Q1178: system-repay via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling which borrowers are placed early versus late in the batch, can an unprivileged attacker make `system-repay` (mainnet/contracts/vault/v0-vault-stx.clar:902) record a repayment larger than the value actually delivered? `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:902` -> `system-repay`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with which borrowers are placed early versus late in the batch varied, and assert that the value `system-repay` returns is identical in both runs; a divergence confirms the finding.
