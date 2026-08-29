# Q1100: system-repay via liquidate: count one deposit as backing for two simultaneous claims

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `min-collateral-expected` reach `system-repay` (mainnet/contracts/vault/v0-vault-stx.clar:902) in a state where it count one deposit as backing for two simultaneous claims? Given that it splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:902` -> `system-repay`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `min-collateral-expected` varied, and assert that the value `system-repay` returns is identical in both runs; a divergence confirms the finding.
