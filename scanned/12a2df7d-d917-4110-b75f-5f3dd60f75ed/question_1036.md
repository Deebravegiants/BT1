# Q1036: inspector verify_block_is_canonical verification and signing disagree

## Question
Can an unprivileged bridge user submitting a malicious foreign-chain transaction or proof payload enter through `verify_foreign_transaction` and use the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing to drive the code path through `crates/foreign-chain-inspector/src/starknet/inspector.rs::verify_block_is_canonical` so that verification and signing disagree on what was actually proven, breaking the invariant that the exact event or transaction proven on the foreign chain must be identical to the object the MPC signs for, and leading to Unauthorized transaction?

## Target
- File/function: crates/foreign-chain-inspector/src/starknet/inspector.rs:92::verify_block_is_canonical
- Entrypoint: `verify_foreign_transaction`
- Attacker controls: the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing
- Exploit idea: verification and signing disagree on what was actually proven
- Invariant to test: the exact event or transaction proven on the foreign chain must be identical to the object the MPC signs for
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: mutate only one component of the proof bundle and verify whether the verification step still passes while the derived signed payload changes
