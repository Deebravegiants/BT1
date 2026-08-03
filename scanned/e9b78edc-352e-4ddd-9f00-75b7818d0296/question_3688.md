# Q3688: set_attribute can leave semantically incomplete success state

## Question
Can an unprivileged attacker make `set_attribute` return success while leaving storage only partially ready for the next public actor, so the next public call misinterprets the object as safely finalized?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_attribute
- Entrypoint: signed extrinsic `set_attribute`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Look for success conditions that are shallow enough to ignore missing cleanup, missing settlement, or missing secondary bookkeeping.
- Invariant to test: A successful call must leave the object in a state that every downstream public consumer can handle safely.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: After each successful edge-case execution, call the next expected public follow-up and check whether it sees a coherent terminal state.
