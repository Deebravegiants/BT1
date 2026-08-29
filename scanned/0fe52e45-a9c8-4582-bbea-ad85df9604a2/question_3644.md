# Q3644: system-repay via repay: make the per-user ledger and the vault aggregate disagree 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls the `ft` trait principal reach `system-repay` (mainnet/contracts/vault/v0-vault-stx.clar:902) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:902` -> `system-repay`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with the `ft` trait principal varied, and assert that the value `system-repay` returns is identical in both runs; a divergence confirms the finding.
