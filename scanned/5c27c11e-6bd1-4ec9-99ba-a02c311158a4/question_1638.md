# Q1638: receive_messages_delivery_proof can create public bridge-state griefing

## Question
Can an unprivileged attacker use `receive_messages_delivery_proof` repeatedly to fill request counters, pending sets, or old-proof buffers until honest bridge progress stalls?

## Target
- File/function: bridges/modules/messages/src/lib.rs::receive_messages_delivery_proof
- Entrypoint: public proof / message submission extrinsic `receive_messages_delivery_proof`
- Attacker controls: proof or signed payload contents
- Exploit idea: Look for public counters or buffers whose exhaustion blocks later valid submissions.
- Invariant to test: Public bridge maintenance paths must not let attackers permanently starve honest progress.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Saturate every public counter and queue near its configured limit, then measure whether honest submissions still succeed.
