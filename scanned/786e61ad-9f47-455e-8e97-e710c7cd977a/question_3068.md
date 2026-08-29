# Q3068: relevant via repay: make the per-user ledger and the vault aggregate disagree 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls the `ft` trait principal reach `relevant` (mainnet/contracts/market/v0-market-vault.clar:175) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it drops any position row whose bit is not present in the enabled mask, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `repay` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `repay` twice with the `ft` trait principal varied, and assert that the value `relevant` returns is identical in both runs; a divergence confirms the finding.
