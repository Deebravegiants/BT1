# Q4532: vault-system-repay via liquidate-multi: mint shares whose backing was never received

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the trait principals supplied per entry reach `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) in a state where it mint shares whose backing was never received? Given that it routes a repayment to one of six vaults by asset id, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the trait principals supplied per entry varied, and assert that the value `vault-system-repay` returns is identical in both runs; a divergence confirms the finding.
