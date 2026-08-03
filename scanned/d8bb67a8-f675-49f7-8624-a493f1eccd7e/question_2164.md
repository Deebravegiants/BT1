# Q2164: execute_overweight can emit misleading queue events

## Question
Can an unprivileged attacker make `execute_overweight` emit success or failure events that disagree with final queue state, enabling secondary claims or repeated execution?

## Target
- File/function: substrate/frame/message-queue/src/lib.rs::execute_overweight
- Entrypoint: public message maintenance extrinsic `execute_overweight`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Look for event generation before the final state transition settles.
- Invariant to test: Queue events must match final execution and payout state exactly.
- Expected Immunefi impact: Repeated execution, fee burn mismatch, or message payout duplication
- Fast validation: Compare event payloads to final queue state and test whether any follow-up public path trusts the event-shaped view.
