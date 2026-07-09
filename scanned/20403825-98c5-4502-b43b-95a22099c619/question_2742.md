# Q2742: foreign chain try_from one parser accepts a

## Question
Can an unprivileged bridge user submitting a malicious foreign-chain transaction or proof payload enter through `verify_foreign_transaction` and use the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing to drive the code path through `crates/near-mpc-contract-interface/src/types/foreign_chain.rs::try_from` so that one parser accepts a payload that another parser would reject or interpret differently, breaking the invariant that all decoders that participate in verification and payload derivation must agree on the normalized transaction, event, and amount fields, and leading to Balance manipulation?

## Target
- File/function: crates/near-mpc-contract-interface/src/types/foreign_chain.rs:454::try_from
- Entrypoint: `verify_foreign_transaction`
- Attacker controls: the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing
- Exploit idea: one parser accepts a payload that another parser would reject or interpret differently
- Invariant to test: all decoders that participate in verification and payload derivation must agree on the normalized transaction, event, and amount fields
- Expected Immunefi impact: Balance manipulation
- Fast validation: fuzz alternate encodings for the same foreign-chain object and diff the normalized values produced at each stage of verification and signing
