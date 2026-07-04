# Q2687: Boundary protocol context can change validation outcome in hashVerKeyVRF

## Question
Can an unprivileged attacker exercise `hashVerKeyVRF` in `libs/cardano-protocol-tpraos/src/Cardano/Protocol/Crypto.hs` via the stated entrypoint and trigger boundary protocol context? The investigation should test whether validation uses one coherent protocol-parameter context from predicate checks through final state update.

## Target
- File/function: libs/cardano-protocol-tpraos/src/Cardano/Protocol/Crypto.hs / hashVerKeyVRF
- Entrypoint: Submit a transaction or block exactly around a protocol parameter, epoch, slot, or era-version boundary.
- Attacker controls: Transaction body, slot/epoch context, protocol parameters, certificates, scripts, witnesses, and block inclusion context.
- Exploit idea: Check whether validation uses one coherent protocol-parameter context from predicate checks through final state update.
- Invariant to test: Ledger predicate consistency: the same transaction or block must receive equivalent acceptance or rejection across mempool, block, and era-specific validation paths.
- Expected Cardano/Intersect impact: Potential High if mempool, block, era, or serialization paths deterministically disagree under normal production validation.
- Fast validation: Construct a mempool-vs-block validation test using the same transaction and assert both paths return the same acceptance result and state delta.
