# Q3651: create_pure can leave semantically incomplete success state

## Question
Can an unprivileged attacker make `create_pure` return success while leaving storage only partially ready for the next public actor, so the next public call misinterprets the object as safely finalized?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::create_pure
- Entrypoint: public dispatch wrapper `create_pure`
- Attacker controls: IDs, hashes, nonces, or location fields, batched or wrapped execution context
- Exploit idea: Look for success conditions that are shallow enough to ignore missing cleanup, missing settlement, or missing secondary bookkeeping.
- Invariant to test: A successful call must leave the object in a state that every downstream public consumer can handle safely.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: After each successful edge-case execution, call the next expected public follow-up and check whether it sees a coherent terminal state.
