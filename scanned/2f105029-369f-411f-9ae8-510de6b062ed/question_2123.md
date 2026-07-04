# Q2123: Memoized bytes can diverge from semantic transaction value in decodeFullDecoder'

## Question
Can an unprivileged attacker exercise `decodeFullDecoder'` in `libs/cardano-ledger-binary/src/Cardano/Ledger/Binary/Decoding.hs` via the stated entrypoint and trigger hash memo bytes instability? The investigation should test whether memoized original bytes drive hashes or IDs while validation uses decoded semantic values, creating witness mismatch or node disagreement.

## Target
- File/function: libs/cardano-ledger-binary/src/Cardano/Ledger/Binary/Decoding.hs / decodeFullDecoder'
- Entrypoint: Submit semantically equivalent but byte-distinct encodings for transaction bodies, witnesses, scripts, metadata, or governance actions.
- Attacker controls: Original encoded bytes, field ordering, optional fields, witness/body bytes, metadata bytes, and script bytes.
- Exploit idea: Check whether memoized original bytes drive hashes or IDs while validation uses decoded semantic values, creating witness mismatch or node disagreement.
- Invariant to test: Canonical encoding invariant: decoded CBOR must have one unambiguous semantic value, stable hashes, stable transaction IDs, and no witness/body mismatch.
- Expected Cardano/Intersect impact: Potential Critical if honest nodes can disagree on transaction or block validity and require hard-fork remediation.
- Fast validation: Create a CBOR round-trip/fuzz test with canonical and non-canonical encodings, then compare decoded values, hashes, transaction IDs, and ledger predicate results.
