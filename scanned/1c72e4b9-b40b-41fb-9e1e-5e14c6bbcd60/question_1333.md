# Q1333: add_candidate_block treats attacker-crafted DID spends as authorized state transitions

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_candidate_block` and control message spends, metadata updates, and current-coin references so that `FullNodeStore.add_candidate_block` in `chia/full_node/full_node_store.py` executes a path where make `add_candidate_block` accept a DID spend or metadata action that is disconnected from the live singleton lineage, violating the invariant that DID message and metadata spends must not bypass current ownership or lineage checks and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_store.py:240 `FullNodeStore.add_candidate_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_candidate_block`
- Attacker controls: message spends, metadata updates, and current-coin references
- Exploit idea: make `add_candidate_block` accept a DID spend or metadata action that is disconnected from the live singleton lineage
- Invariant to test: DID message and metadata spends must not bypass current ownership or lineage checks
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: submit DID spend/message edge cases to `chia/full_node/full_node_store.py:add_candidate_block` and assert current-coin and lineage checks gate every state mutation
