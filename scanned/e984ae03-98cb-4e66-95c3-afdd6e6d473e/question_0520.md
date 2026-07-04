# Q520: Datum lookup can disagree between reference inputs and spending inputs in toJSON

## Question
Can an unprivileged attacker exercise `toJSON` in `eras/babbage/impl/src/Cardano/Ledger/Babbage/TxInfo.hs` via the stated entrypoint and trigger datum and reference input lookup mismatch? The investigation should test whether datum availability or lookup uses different acceptable datum sets across script context creation and UTXOW validation.

## Target
- File/function: eras/babbage/impl/src/Cardano/Ledger/Babbage/TxInfo.hs / toJSON
- Entrypoint: Submit a transaction using reference inputs, spending inputs, inline datums, datum hashes, and supplemental datums with overlapping hashes.
- Attacker controls: Reference inputs, spending inputs, TxOut datums, witness datums, redeemers, scripts, and input ordering.
- Exploit idea: Check whether datum availability or lookup uses different acceptable datum sets across script context creation and UTXOW validation.
- Invariant to test: Script validation invariant: phase-1 witnesses and phase-2 Plutus evaluation, redeemers, datums, reference scripts, collateral, and validity flags must agree on acceptance and accounting.
- Expected Cardano/Intersect impact: Potential High if mempool, block, era, or serialization paths deterministically disagree under normal production validation.
- Fast validation: Create a transaction-level Plutus validation test with controlled redeemers, datums, execution units, collateral, and script validity flag, then assert accounting and predicate consistency.
