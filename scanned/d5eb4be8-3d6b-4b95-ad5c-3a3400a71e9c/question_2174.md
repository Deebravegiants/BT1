# Q2174: composition of submit_delivery_receipt can violate local assumptions

## Question
Can an unprivileged attacker wrap `submit_delivery_receipt` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: bridges/snowbridge/pallets/outbound-queue-v2/src/lib.rs::submit_delivery_receipt
- Entrypoint: public proof / message submission extrinsic `submit_delivery_receipt`
- Attacker controls: proof or signed payload contents
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
