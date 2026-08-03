# Q2189: composition of eth_transact can violate local assumptions

## Question
Can an unprivileged attacker wrap `eth_transact` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/revive/src/lib.rs::eth_transact
- Entrypoint: public VM / contract execution extrinsic `eth_transact`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Unauthorized code/call execution or theft from contract-controlled funds
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
