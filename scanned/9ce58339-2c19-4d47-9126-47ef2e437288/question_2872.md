# Q2872: foreign chain whitelist verifier compare_chain a disallowed provider or

## Question
Can an unprivileged bridge user submitting a malicious foreign-chain transaction or proof payload enter through `verify_foreign_transaction` and use the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing to drive the code path through `crates/node/src/foreign_chain_whitelist_verifier.rs::compare_chain` so that a disallowed provider or chain slips into the effective verification set, breaking the invariant that the runtime verifier must use the same allowlist and routing semantics that governance approved, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/foreign_chain_whitelist_verifier.rs:120::compare_chain
- Entrypoint: `verify_foreign_transaction`
- Attacker controls: the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing
- Exploit idea: a disallowed provider or chain slips into the effective verification set
- Invariant to test: the runtime verifier must use the same allowlist and routing semantics that governance approved
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: update allowed providers or supported chains around a live request and diff the governance-visible configuration against what runtime verification actually uses
