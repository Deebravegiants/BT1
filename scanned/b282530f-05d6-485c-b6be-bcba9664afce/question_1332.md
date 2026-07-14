# Q1332: add_candidate_block accepts a DID recovery or transfer path with attacker-controlled lineage

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_candidate_block` and control backup, recovery, transfer, and parent-lineage inputs so that `FullNodeStore.add_candidate_block` in `chia/full_node/full_node_store.py` executes a path where make `add_candidate_block` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority, violating the invariant that DID recovery and transfer authority must derive from the live singleton lineage only and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_store.py:240 `FullNodeStore.add_candidate_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_candidate_block`
- Attacker controls: backup, recovery, transfer, and parent-lineage inputs
- Exploit idea: make `add_candidate_block` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority
- Invariant to test: DID recovery and transfer authority must derive from the live singleton lineage only
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: replay attacker-crafted DID backup or recovery material into `chia/full_node/full_node_store.py:add_candidate_block` and assert recovery fails without live authority
