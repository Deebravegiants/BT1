# Q0608: ubalance via deposit: destroy value through a truncation the opposite operation 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `recipient`, including a contract principal reach `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `recipient`, including a contract principal varied, and assert that the value `ubalance` returns is identical in both runs; a divergence confirms the finding.
