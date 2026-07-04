# Q2993: Boundary output size can pass with insufficient minimum ADA in getAlonzoScriptsHashesNeeded

## Question
Can an unprivileged attacker exercise `getAlonzoScriptsHashesNeeded` in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/UTxO.hs` via the stated entrypoint and trigger min-ADA or output size boundary? The investigation should test whether serialized size, value size, and minimum-ADA calculations disagree so an output below the required minimum can enter the UTxO or a valid output is rejected.

## Target
- File/function: eras/alonzo/impl/src/Cardano/Ledger/Alonzo/UTxO.hs / getAlonzoScriptsHashesNeeded
- Entrypoint: Submit a transaction with boundary-sized outputs, nested assets, inline datums, reference scripts, and minimum-ADA-adjacent coin values.
- Attacker controls: TxOut value, datum option, reference script, asset names, policy IDs, output count, fee, and protocol parameter era.
- Exploit idea: Check whether serialized size, value size, and minimum-ADA calculations disagree so an output below the required minimum can enter the UTxO or a valid output is rejected.
- Invariant to test: Value conservation: consumed value plus withdrawals plus minted value must equal produced value plus fees plus deposits plus treasury/reserve movement under the era rules.
- Expected Cardano/Intersect impact: Potential Medium if an unprivileged user can trigger incorrect fees, deposits, refunds, rewards, withdrawals, treasury movement, or validation limits without full chain split.
- Fast validation: Write a focused ledger unit/property test constructing the transaction or state transition and assert the predicate failure or final state matches the invariant.
