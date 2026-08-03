# Q0295: receive_messages_proof can undercharge proof verification

## Question
Can an unprivileged attacker use `receive_messages_proof` with crafted proof or signed payload contents so the call pays for less verification or dispatch work than it actually triggers?

## Target
- File/function: bridges/modules/messages/src/lib.rs::receive_messages_proof
- Entrypoint: public proof / message submission extrinsic `receive_messages_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Probe declared counts, weights, vector sizes, and payload sizes against real proof complexity.
- Invariant to test: Worst-case verification and dispatch work must remain within charged weight.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Fuzz maximal proof sizes, message counts, header ancestries, and dispatch weight declarations.
