# Q3526: eth_substrate_call can leave semantically incomplete success state

## Question
Can an unprivileged attacker make `eth_substrate_call` return success while leaving storage only partially ready for the next public actor, so the next public call misinterprets the object as safely finalized?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_substrate_call
- Entrypoint: public VM / contract execution extrinsic `eth_substrate_call`
- Attacker controls: nested call payloads, duplicate or adversarial list ordering
- Exploit idea: Look for success conditions that are shallow enough to ignore missing cleanup, missing settlement, or missing secondary bookkeeping.
- Invariant to test: A successful call must leave the object in a state that every downstream public consumer can handle safely.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: After each successful edge-case execution, call the next expected public follow-up and check whether it sees a coherent terminal state.
