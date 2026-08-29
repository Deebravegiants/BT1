# Q0200: zip via redeem: destroy value through a truncation the opposite operation 

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the gap between the `assets` var and the real balance reach `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it pairs the utilization and rate point lists element by element, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `redeem` twice with the gap between the `assets` var and the real balance varied, and assert that the value `zip` returns is identical in both runs; a divergence confirms the finding.
