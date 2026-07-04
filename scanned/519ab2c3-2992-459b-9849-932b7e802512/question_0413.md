# Q413: Script failure collateral can be accounted differently than fee checks in Signal

## Question
Can an unprivileged attacker exercise `Signal` in `eras/babbage/impl/src/Cardano/Ledger/Babbage/Rules/Utxos.hs` via the stated entrypoint and trigger Plutus collateral return mismatch? The investigation should test whether collateral collection, collateral return, and fee sufficiency are computed from inconsistent values or branches when phase-2 validation fails.

## Target
- File/function: eras/babbage/impl/src/Cardano/Ledger/Babbage/Rules/Utxos.hs / Signal
- Entrypoint: Submit a transaction with a failing Plutus script, collateral inputs, collateral return, total collateral, reference inputs, and boundary fee values.
- Attacker controls: Collateral inputs, collateral return output, total collateral field, fee, redeemers, datums, reference inputs, script validity flag, and ExUnits.
- Exploit idea: Check whether collateral collection, collateral return, and fee sufficiency are computed from inconsistent values or branches when phase-2 validation fails.
- Invariant to test: Script validation invariant: phase-1 witnesses and phase-2 Plutus evaluation, redeemers, datums, reference scripts, collateral, and validity flags must agree on acceptance and accounting.
- Expected Cardano/Intersect impact: Potential Critical if value conservation is broken and ADA or native assets can be created, destroyed, or permanently frozen.
- Fast validation: Create a transaction-level Plutus validation test with controlled redeemers, datums, execution units, collateral, and script validity flag, then assert accounting and predicate consistency.
