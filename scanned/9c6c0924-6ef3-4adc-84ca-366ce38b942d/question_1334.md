# Q1334: add_candidate_block accepts stale DID lineage in a live authority path

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_candidate_block` and control stale DID parent or lineage state replayed into a live DID path so that `FullNodeStore.add_candidate_block` in `chia/full_node/full_node_store.py` executes a path where make `add_candidate_block` accept stale DID lineage or parent state during a live authority transition, violating the invariant that stale DID parent or lineage state must not authorize live DID actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_store.py:240 `FullNodeStore.add_candidate_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_candidate_block`
- Attacker controls: stale DID parent or lineage state replayed into a live DID path
- Exploit idea: make `add_candidate_block` accept stale DID lineage or parent state during a live authority transition
- Invariant to test: stale DID parent or lineage state must not authorize live DID actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: feed stale parent or lineage data into `chia/full_node/full_node_store.py:add_candidate_block` during a live DID update and assert no authority bypass occurs
