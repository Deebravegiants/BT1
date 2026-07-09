# Q2467: foreign chains metadata snapshot_by_node a proof or transaction

## Question
Can an unprivileged bridge user submitting a malicious foreign-chain transaction or proof payload enter through `verify_foreign_transaction` and use the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing to drive the code path through `crates/contract/src/foreign_chains_metadata.rs::snapshot_by_node` so that a proof or transaction can be replayed across chains, providers, or domains, breaking the invariant that signed approval must bind chain identity, transaction identity, finality context, and domain-specific signing scope, and leading to Cross-chain replay attacks enabling double-spending?

## Target
- File/function: crates/contract/src/foreign_chains_metadata.rs:82::snapshot_by_node
- Entrypoint: `verify_foreign_transaction`
- Attacker controls: the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing
- Exploit idea: a proof or transaction can be replayed across chains, providers, or domains
- Invariant to test: signed approval must bind chain identity, transaction identity, finality context, and domain-specific signing scope
- Expected Immunefi impact: Cross-chain replay attacks enabling double-spending
- Fast validation: reuse one foreign-chain transaction or proof under a second chain/domain/provider interpretation and compare the signed payload bytes
