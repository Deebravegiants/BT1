# Q2196: composition of swap_tokens_for_exact_tokens can violate local assumptions

## Question
Can an unprivileged attacker wrap `swap_tokens_for_exact_tokens` inside other public user-controlled flows such as batching, proxying, multisig, or relayed execution and break assumptions the implementation makes about single-step execution?

## Target
- File/function: substrate/frame/asset-conversion/src/lib.rs::swap_tokens_for_exact_tokens
- Entrypoint: signed extrinsic `swap_tokens_for_exact_tokens`
- Attacker controls: amounts, fees, or prices, duplicate or adversarial list ordering
- Exploit idea: Exercise the same entrypoint inside richer public execution contexts that preserve user control but alter ordering, effective caller plumbing, or failure boundaries.
- Invariant to test: The call must preserve its core authorization, accounting, and rollback invariants even when composed inside other public wrappers.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Run the entrypoint directly, then through batch, proxy, multisig, or meta-transaction style wrappers and diff storage, events, and charging.
