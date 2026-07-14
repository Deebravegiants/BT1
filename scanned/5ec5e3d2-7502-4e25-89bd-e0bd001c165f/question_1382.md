# Q1382: new_tx_block lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_tx_block` and control a sequence of conflicting but protocol-valid spends and arrival order so that `Mempool.new_tx_block` in `chia/full_node/mempool.py` executes a path where abuse conflict handling inside `new_tx_block` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/full_node/mempool.py:329 `Mempool.new_tx_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_tx_block`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `new_tx_block` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/full_node/mempool.py:new_tx_block` and assert a valid honest spend eventually processes under bounded attacker traffic
