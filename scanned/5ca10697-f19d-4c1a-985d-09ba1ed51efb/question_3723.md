# Q3723: check_status can leave semantically incomplete success state

## Question
Can an unprivileged attacker make `check_status` return success while leaving storage only partially ready for the next public actor, so the next public call misinterprets the object as safely finalized?

## Target
- File/function: substrate/frame/treasury/src/lib.rs::check_status
- Entrypoint: signed extrinsic `check_status`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for success conditions that are shallow enough to ignore missing cleanup, missing settlement, or missing secondary bookkeeping.
- Invariant to test: A successful call must leave the object in a state that every downstream public consumer can handle safely.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: After each successful edge-case execution, call the next expected public follow-up and check whether it sees a coherent terminal state.
