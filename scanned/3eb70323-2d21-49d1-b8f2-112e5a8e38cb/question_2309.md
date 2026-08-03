# Q2309: composition of note_preimage can violate local assumptions

## Question
Can an unprivileged attacker wrap `note_preimage` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/preimage/src/lib.rs::note_preimage
- Entrypoint: signed extrinsic `note_preimage`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
