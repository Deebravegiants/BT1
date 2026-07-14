# Q1181: register_for_coin_updates lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach P2P message handler `register_for_coin_updates` and control a sequence of conflicting but protocol-valid spends and arrival order so that `FullNodeAPI.register_for_coin_updates` in `chia/full_node/full_node_api.py` executes a path where abuse conflict handling inside `register_for_coin_updates` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/full_node/full_node_api.py:1890 `FullNodeAPI.register_for_coin_updates`
- Entrypoint: P2P message handler `register_for_coin_updates`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `register_for_coin_updates` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/full_node/full_node_api.py:register_for_coin_updates` and assert a valid honest spend eventually processes under bounded attacker traffic
