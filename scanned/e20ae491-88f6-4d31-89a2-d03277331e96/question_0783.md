# Q783: Per-transaction checks can miss block-level aggregate limits in Cardano.Chain.UTxO

## Question
Can an unprivileged attacker exercise `Cardano.Chain.UTxO` in `eras/byron/ledger/impl/src/Cardano/Chain/UTxO.hs` via the stated entrypoint and trigger block body aggregate limit bypass? The investigation should test whether per-transaction validation and block-body validation compute aggregate limits from different UTxO snapshots or transaction orderings.

## Target
- File/function: eras/byron/ledger/impl/src/Cardano/Chain/UTxO.hs / Cardano.Chain.UTxO
- Entrypoint: Produce a block candidate containing individually valid transactions whose combined reference scripts, sizes, ex-units, or certificates hit aggregate boundaries.
- Attacker controls: Transaction sequence, reference scripts, input ordering, script validity flags, block body contents, and transaction sizes.
- Exploit idea: Check whether per-transaction validation and block-body validation compute aggregate limits from different UTxO snapshots or transaction orderings.
- Invariant to test: Resource-limit invariant: attacker-controlled transaction, certificate, vote, proposal, script, and CBOR sizes must be bounded consistently before expensive ledger work.
- Expected Cardano/Intersect impact: Potential High if mempool, block, era, or serialization paths deterministically disagree under normal production validation.
- Fast validation: Construct a mempool-vs-block validation test using the same transaction and assert both paths return the same acceptance result and state delta.
