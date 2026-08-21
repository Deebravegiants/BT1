# Q1924: Failure to bind capture artifacts to the consenting identity in handle_save_ir_net_estimate (agents/image_notary.rs)

## Question
Can an unprivileged attacker make `handle_save_ir_net_estimate` in [src/agents/image_notary.rs](src/agents/image_notary.rs) associate capture artifacts with the identity that is *currently* set rather than the one that was validated when the frames were captured, so a late identity change re-attributes earlier frames?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `handle_save_ir_net_estimate` (function)
- Entrypoint: Changing the scanned identity after capture has begun
- Attacker controls: the ordering of the identity scan relative to capture
- Exploit idea: Check whether `handle_save_ir_net_estimate` snapshots the identity at capture time or reads it at packaging time.
- Invariant to test: Artifacts are bound to the identity validated at their capture instant, immutably.
- Expected Immunefi impact: Another person's captured frames packaged under the attacker's identity
- Fast validation: Integration test changing identity mid-flow and asserting artifacts keep their capture-time binding.
