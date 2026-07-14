# Q1118: send_transaction lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach P2P message handler `send_transaction` and control a sequence of conflicting but protocol-valid spends and arrival order so that `FullNodeAPI.send_transaction` in `chia/full_node/full_node_api.py` executes a path where abuse conflict handling inside `send_transaction` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/full_node/full_node_api.py:1554 `FullNodeAPI.send_transaction`
- Entrypoint: P2P message handler `send_transaction`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `send_transaction` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/full_node/full_node_api.py:send_transaction` and assert a valid honest spend eventually processes under bounded attacker traffic
