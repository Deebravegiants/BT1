# Q2262: composition of create_with_pool_id can violate local assumptions

## Question
Can an unprivileged attacker wrap `create_with_pool_id` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::create_with_pool_id
- Entrypoint: signed extrinsic `create_with_pool_id`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
