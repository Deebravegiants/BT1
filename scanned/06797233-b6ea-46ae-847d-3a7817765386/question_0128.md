# Q0128: lookup via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `receiver`, including a contract principal reach `lookup` (mainnet/contracts/registry/v0-assets.clar:139) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns the registry record, including the `decimals` captured once at registration, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `receiver`, including a contract principal varied, and assert that the value `lookup` returns is identical in both runs; a divergence confirms the finding.
