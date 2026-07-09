# Q2471: foreign chains metadata snapshot_by_node a verification result authorizes

## Question
Can an unprivileged bridge user submitting a malicious foreign-chain transaction or proof payload enter through `verify_foreign_transaction` and use the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing to drive the code path through `crates/contract/src/foreign_chains_metadata.rs::snapshot_by_node` so that a verification result authorizes a different user-supplied transfer intent, breaking the invariant that verification results must stay bound to the exact request that created them, including chain, tx identity, user, and domain, and leading to Theft or permanent freezing of funds?

## Target
- File/function: crates/contract/src/foreign_chains_metadata.rs:82::snapshot_by_node
- Entrypoint: `verify_foreign_transaction`
- Attacker controls: the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing
- Exploit idea: a verification result authorizes a different user-supplied transfer intent
- Invariant to test: verification results must stay bound to the exact request that created them, including chain, tx identity, user, and domain
- Expected Immunefi impact: Theft or permanent freezing of funds
- Fast validation: submit near-identical verification requests concurrently, complete only one proof path, and inspect whether both requests can be resolved or the wrong request resolves
