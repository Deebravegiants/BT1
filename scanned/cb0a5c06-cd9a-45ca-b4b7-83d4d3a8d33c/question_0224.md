# Q0224: relevant via collateral-add: destroy value through a truncation the opposite operation 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `relevant` (mainnet/contracts/market/v0-market-vault.clar:175) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it drops any position row whose bit is not present in the enabled mask, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with `amount` varied, and assert that the value `relevant` returns is identical in both runs; a divergence confirms the finding.
