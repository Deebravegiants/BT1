# Q0004: receive_messages_delivery_proof can replay a previously accepted proof

## Question
Can an unprivileged attacker or relayer call `receive_messages_delivery_proof` twice with the same underlying proof, event, header, or commitment and make bridge state advance or a payout happen twice?

## Target
- File/function: bridges/modules/messages/src/lib.rs::receive_messages_delivery_proof
- Entrypoint: public proof / message submission extrinsic `receive_messages_delivery_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Search for proof identifiers that are only partially bound to monotonic bridge state.
- Invariant to test: Each bridged proof, receipt, header, and message nonce must be accepted at most once.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Submit one valid object, then replay it byte-for-byte and with minimally changed declared metadata.
