# Q2375: composition of unlock can violate local assumptions

## Question
Can an unprivileged attacker wrap `unlock` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/conviction-voting/src/lib.rs::unlock
- Entrypoint: signed extrinsic `unlock`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
