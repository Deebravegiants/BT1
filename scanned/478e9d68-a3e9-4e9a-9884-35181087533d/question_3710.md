# Q3710: split_coins lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach RPC route `split_coins` and control a sequence of conflicting but protocol-valid spends and arrival order so that `WalletRpcApi.split_coins` in `chia/wallet/wallet_rpc_api.py` executes a path where abuse conflict handling inside `split_coins` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1415 `WalletRpcApi.split_coins`
- Entrypoint: RPC route `split_coins`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `split_coins` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/wallet/wallet_rpc_api.py:split_coins` and assert a valid honest spend eventually processes under bounded attacker traffic
