# Q1895: key state public_key mixed-epoch state makes the

## Question
Can an unprivileged NEAR account enter through `public_key` and use the chosen predecessor override, derivation path, queried domain or curve, and timing relative to key-version changes to drive the code path through `crates/contract/src/primitives/key_state.rs::public_key` so that mixed-epoch state makes the contract accept a completion that should be invalid for the current authority set, breaking the invariant that validation epoch, key version, and completion epoch must stay consistent for one logical request, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/contract/src/primitives/key_state.rs:47::public_key
- Entrypoint: `public_key`
- Attacker controls: the chosen predecessor override, derivation path, queried domain or curve, and timing relative to key-version changes
- Exploit idea: mixed-epoch state makes the contract accept a completion that should be invalid for the current authority set
- Invariant to test: validation epoch, key version, and completion epoch must stay consistent for one logical request
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: race a real request against domain/key-version changes and compare the epoch used at enqueue time to the epoch used at response resolution
