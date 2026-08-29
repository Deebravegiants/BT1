# Q5888: vault-system-borrow via repay: have the same quantity scaled twice by two contracts that 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `on-behalf-of`, naming any third-party principal reach `vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it routes a borrow to one of six vaults by asset id, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `on-behalf-of`, naming any third-party principal varied, and assert that the value `vault-system-borrow` returns is identical in both runs; a divergence confirms the finding.
