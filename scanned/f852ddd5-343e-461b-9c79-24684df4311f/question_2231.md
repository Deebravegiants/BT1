# Q2231: composition of create_swap can violate local assumptions

## Question
Can an unprivileged attacker wrap `create_swap` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/atomic-swap/src/lib.rs::create_swap
- Entrypoint: signed extrinsic `create_swap`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
