# Q3544: clear_metadata can leave semantically incomplete success state

## Question
Can an unprivileged attacker make `clear_metadata` return success while leaving storage only partially ready for the next public actor, so the next public call misinterprets the object as safely finalized?

## Target
- File/function: substrate/frame/assets/src/lib.rs::clear_metadata
- Entrypoint: signed extrinsic `clear_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for success conditions that are shallow enough to ignore missing cleanup, missing settlement, or missing secondary bookkeeping.
- Invariant to test: A successful call must leave the object in a state that every downstream public consumer can handle safely.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: After each successful edge-case execution, call the next expected public follow-up and check whether it sees a coherent terminal state.
