# Q0002: submit_finality_proof can replay a previously accepted proof

## Question
Can an unprivileged attacker or relayer call `submit_finality_proof` twice with the same underlying proof, event, header, or commitment and make bridge state advance or a payout happen twice?

## Target
- File/function: bridges/modules/grandpa/src/lib.rs::submit_finality_proof
- Entrypoint: public proof / message submission extrinsic `submit_finality_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Search for proof identifiers that are only partially bound to monotonic bridge state.
- Invariant to test: Each bridged proof, receipt, header, and message nonce must be accepted at most once.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Submit one valid object, then replay it byte-for-byte and with minimally changed declared metadata.
