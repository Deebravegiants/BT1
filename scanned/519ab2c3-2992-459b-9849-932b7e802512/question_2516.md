# Q2516: Script validity flag can select inconsistent ledger accounting branch in Cardano.Ledger.Plutus

## Question
Can an unprivileged attacker exercise `Cardano.Ledger.Plutus` in `libs/cardano-ledger-core/src/Cardano/Ledger/Plutus.hs` via the stated entrypoint and trigger script validity flag branch disagreement? The investigation should test whether the implementation accepts a branch where phase-1 validation, phase-2 evaluation, and accounting disagree about whether normal outputs or collateral outputs are applied.

## Target
- File/function: libs/cardano-ledger-core/src/Cardano/Ledger/Plutus.hs / Cardano.Ledger.Plutus
- Entrypoint: Submit a transaction whose script validity flag, redeemers, datums, witnesses, and reference scripts are arranged around phase-1/phase-2 boundary cases.
- Attacker controls: isValid flag, script witnesses, reference scripts, redeemers, datums, collateral, fee, and input sets.
- Exploit idea: Check whether the implementation accepts a branch where phase-1 validation, phase-2 evaluation, and accounting disagree about whether normal outputs or collateral outputs are applied.
- Invariant to test: Script validation invariant: phase-1 witnesses and phase-2 Plutus evaluation, redeemers, datums, reference scripts, collateral, and validity flags must agree on acceptance and accounting.
- Expected Cardano/Intersect impact: Potential Critical if honest nodes can disagree on transaction or block validity and require hard-fork remediation.
- Fast validation: Create a transaction-level Plutus validation test with controlled redeemers, datums, execution units, collateral, and script validity flag, then assert accounting and predicate consistency.
