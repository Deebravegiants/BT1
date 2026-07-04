# Q3290: Bootstrap witness or address network checks can diverge across eras in Error

## Question
Can an unprivileged attacker exercise `Error` in `eras/byron/ledger/impl/src/Cardano/Chain/Delegation/Validation/Scheduling.hs` via the stated entrypoint and trigger bootstrap witness network mismatch? The investigation should test whether legacy address/witness validation and modern UTXOW network checks disagree, accepting a spend under one path but rejecting under another.

## Target
- File/function: eras/byron/ledger/impl/src/Cardano/Chain/Delegation/Validation/Scheduling.hs / Error
- Entrypoint: Submit a transaction spending legacy or bootstrap-address UTxO with boundary network magic, address attributes, and witness encodings.
- Attacker controls: Bootstrap witness bytes, address attributes, network ID, transaction body hash, inputs, outputs, and witness set.
- Exploit idea: Check whether legacy address/witness validation and modern UTXOW network checks disagree, accepting a spend under one path but rejecting under another.
- Invariant to test: Ledger predicate consistency: the same transaction or block must receive equivalent acceptance or rejection across mempool, block, and era-specific validation paths.
- Expected Cardano/Intersect impact: Potential High if mempool, block, era, or serialization paths deterministically disagree under normal production validation.
- Fast validation: Write a focused ledger unit/property test constructing the transaction or state transition and assert the predicate failure or final state matches the invariant.
