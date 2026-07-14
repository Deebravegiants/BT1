# Q1428: create_bundle_from_mempool_items lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `create_bundle_from_mempool_items` and control a sequence of conflicting but protocol-valid spends and arrival order so that `Mempool.create_bundle_from_mempool_items` in `chia/full_node/mempool.py` executes a path where abuse conflict handling inside `create_bundle_from_mempool_items` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/full_node/mempool.py:583 `Mempool.create_bundle_from_mempool_items`
- Entrypoint: full node mempool, sync, or peer flow reaching `create_bundle_from_mempool_items`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `create_bundle_from_mempool_items` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/full_node/mempool.py:create_bundle_from_mempool_items` and assert a valid honest spend eventually processes under bounded attacker traffic
