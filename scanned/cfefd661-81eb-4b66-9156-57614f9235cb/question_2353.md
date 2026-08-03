# Q2353: composition of set_collection_metadata can violate local assumptions

## Question
Can an unprivileged attacker wrap `set_collection_metadata` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/nfts/src/lib.rs::set_collection_metadata
- Entrypoint: signed extrinsic `set_collection_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Unauthorized NFT or fractional-asset transfer / unbacked mint
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
