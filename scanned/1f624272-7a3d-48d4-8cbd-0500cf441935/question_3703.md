# Q3703: set_instance_metadata can leave semantically incomplete success state

## Question
Can an unprivileged attacker make `set_instance_metadata` return success while leaving storage only partially ready for the next public actor, so the next public call misinterprets the object as safely finalized?

## Target
- File/function: substrate/frame/scarcity/src/lib.rs::set_instance_metadata
- Entrypoint: signed extrinsic `set_instance_metadata`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Look for success conditions that are shallow enough to ignore missing cleanup, missing settlement, or missing secondary bookkeeping.
- Invariant to test: A successful call must leave the object in a state that every downstream public consumer can handle safely.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: After each successful edge-case execution, call the next expected public follow-up and check whether it sees a coherent terminal state.
