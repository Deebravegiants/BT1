# Q23: lib verify_foreign_transaction mixed-epoch state makes the

## Question
Can an unprivileged NEAR account enter through `verify_foreign_transaction` and use the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing to drive the code path through `crates/contract/src/lib.rs::verify_foreign_transaction` so that mixed-epoch state makes the contract accept a completion that should be invalid for the current authority set, breaking the invariant that validation epoch, key version, and completion epoch must stay consistent for one logical request, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/contract/src/lib.rs:519::verify_foreign_transaction
- Entrypoint: `verify_foreign_transaction`
- Attacker controls: the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing
- Exploit idea: mixed-epoch state makes the contract accept a completion that should be invalid for the current authority set
- Invariant to test: validation epoch, key version, and completion epoch must stay consistent for one logical request
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: race a real request against domain/key-version changes and compare the epoch used at enqueue time to the epoch used at response resolution
