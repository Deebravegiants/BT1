# Q2986: Duplicate CBOR map keys can change transaction semantics or hashes in unRedeemersL

## Question
Can an unprivileged attacker exercise `unRedeemersL` in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/TxWits.hs` via the stated entrypoint and trigger CBOR duplicate map key semantic ambiguity? The investigation should test whether decoding chooses one value while hashing, witnesses, CDDL expectations, or ledger predicates assume another canonical value.

## Target
- File/function: eras/alonzo/impl/src/Cardano/Ledger/Alonzo/TxWits.hs / unRedeemersL
- Entrypoint: Submit malformed-but-decodable CBOR containing duplicate keys or semantically equivalent encodings for transaction bodies, witnesses, metadata, or governance objects.
- Attacker controls: CBOR map keys, field order, optional fields, duplicate fields, witness set encoding, metadata, and transaction body bytes.
- Exploit idea: Check whether decoding chooses one value while hashing, witnesses, CDDL expectations, or ledger predicates assume another canonical value.
- Invariant to test: Canonical encoding invariant: decoded CBOR must have one unambiguous semantic value, stable hashes, stable transaction IDs, and no witness/body mismatch.
- Expected Cardano/Intersect impact: Potential Critical if honest nodes can disagree on transaction or block validity and require hard-fork remediation.
- Fast validation: Create a CBOR round-trip/fuzz test with canonical and non-canonical encodings, then compare decoded values, hashes, transaction IDs, and ledger predicate results.
