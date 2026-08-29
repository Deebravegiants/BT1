# Q3320: calc-multiplier-delta via deposit: make the per-user ledger and the vault aggregate disagree 

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `recipient`, including a contract principal reach `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it compounds a rate over `time-delta` with a caller-independent rounding flag, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `deposit` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `recipient`, including a contract principal varied, and assert that the value `calc-multiplier-delta` returns is identical in both runs; a divergence confirms the finding.
