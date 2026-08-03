# Q3505: submit_finality_proof can leave semantically incomplete success state

## Question
Can an unprivileged attacker make `submit_finality_proof` return success while leaving storage only partially ready for the next public actor, so the next public call misinterprets the object as safely finalized?

## Target
- File/function: bridges/modules/grandpa/src/lib.rs::submit_finality_proof
- Entrypoint: public proof / message submission extrinsic `submit_finality_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Look for success conditions that are shallow enough to ignore missing cleanup, missing settlement, or missing secondary bookkeeping.
- Invariant to test: A successful call must leave the object in a state that every downstream public consumer can handle safely.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: After each successful edge-case execution, call the next expected public follow-up and check whether it sees a coherent terminal state.
