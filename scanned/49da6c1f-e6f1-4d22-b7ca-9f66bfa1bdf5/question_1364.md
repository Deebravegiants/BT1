# Q1364: system-repay via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `system-repay` (mainnet/contracts/vault/v0-vault-stx.clar:902) in a state where it count one deposit as backing for two simultaneous claims? Given that it splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:902` -> `system-repay`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `ft` trait principal varied, and assert that the value `system-repay` returns is identical in both runs; a divergence confirms the finding.
