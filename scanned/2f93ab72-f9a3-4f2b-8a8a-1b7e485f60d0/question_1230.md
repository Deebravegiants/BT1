# Q1230: Redeemer pointer mapping can bind to the wrong script purpose in scriptPrefixTag

## Question
Can an unprivileged attacker exercise `scriptPrefixTag` in `eras/conway/impl/src/Cardano/Ledger/Conway/Scripts.hs` via the stated entrypoint and trigger redeemer pointer indexing ambiguity? The investigation should test whether redeemer indexing or inverse mapping can attach a redeemer to the wrong purpose after ordering, duplication, or omission of adjacent purposes.

## Target
- File/function: eras/conway/impl/src/Cardano/Ledger/Conway/Scripts.hs / scriptPrefixTag
- Entrypoint: Submit a transaction with multiple certificates, withdrawals, mints, votes, proposals, and spending scripts that create boundary redeemer indexes.
- Attacker controls: Redeemer map, script purpose order, certificates, withdrawals, mint policies, voting/proposal procedures, inputs, and reference scripts.
- Exploit idea: Check whether redeemer indexing or inverse mapping can attach a redeemer to the wrong purpose after ordering, duplication, or omission of adjacent purposes.
- Invariant to test: Script validation invariant: phase-1 witnesses and phase-2 Plutus evaluation, redeemers, datums, reference scripts, collateral, and validity flags must agree on acceptance and accounting.
- Expected Cardano/Intersect impact: Potential High if mempool, block, era, or serialization paths deterministically disagree under normal production validation.
- Fast validation: Create a transaction-level Plutus validation test with controlled redeemers, datums, execution units, collateral, and script validity flag, then assert accounting and predicate consistency.
