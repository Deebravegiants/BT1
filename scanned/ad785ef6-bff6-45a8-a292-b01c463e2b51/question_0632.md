# Q0632: increment via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `increment` (mainnet/contracts/market/v0-market-vault.clar:137) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it advances the user-id nonce, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `increment` advances the user-id nonce. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `increment` returns is identical in both runs; a divergence confirms the finding.
