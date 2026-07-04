# Q1120: Era transition can drop deposits, rewards, or governance obligations in PredicateFailure

## Question
Can an unprivileged attacker exercise `PredicateFailure` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/HardFork.hs` via the stated entrypoint and trigger era transition drops ledger obligation? The investigation should test whether translation preserves all obligations and constraints, especially fields removed, renamed, newly initialized, or interpreted differently in the next era.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/HardFork.hs / PredicateFailure
- Entrypoint: Reach an era boundary with UTxO, deposits, rewards, certificates, scripts, protocol parameters, or governance state set to boundary values.
- Attacker controls: Pre-transition ledger state through valid transactions, certificates, withdrawals, scripts, governance actions, and protocol update timing.
- Exploit idea: Check whether translation preserves all obligations and constraints, especially fields removed, renamed, newly initialized, or interpreted differently in the next era.
- Invariant to test: Era transition invariant: translated ledger state must preserve spendability, deposits, rewards, protocol parameters, script semantics, and hashes across hard-fork boundaries.
- Expected Cardano/Intersect impact: Potential Critical if honest nodes can disagree on transaction or block validity and require hard-fork remediation.
- Fast validation: Run an era-specific model/differential test comparing the implementation result with the expected STS transition and final ledger accounting.
