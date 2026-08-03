# Q2256: composition of bond_extra can violate local assumptions

## Question
Can an unprivileged attacker wrap `bond_extra` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::bond_extra
- Entrypoint: signed extrinsic `bond_extra`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
