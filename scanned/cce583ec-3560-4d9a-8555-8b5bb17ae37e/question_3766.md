# Q3766: get_coin_records_by_names lets crafted conflicts block valid spends for too long

## Question
Can an unprivileged attacker reach RPC route `get_coin_records_by_names` and control a sequence of conflicting but protocol-valid spends and arrival order so that `WalletRpcApi.get_coin_records_by_names` in `chia/wallet/wallet_rpc_api.py` executes a path where abuse conflict handling inside `get_coin_records_by_names` so honest valid spends stay excluded while attacker-controlled conflicts cycle, violating the invariant that an attacker must not be able to keep honest valid spends out of processing under normal network assumptions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1753 `WalletRpcApi.get_coin_records_by_names`
- Entrypoint: RPC route `get_coin_records_by_names`
- Attacker controls: a sequence of conflicting but protocol-valid spends and arrival order
- Exploit idea: abuse conflict handling inside `get_coin_records_by_names` so honest valid spends stay excluded while attacker-controlled conflicts cycle
- Invariant to test: an attacker must not be able to keep honest valid spends out of processing under normal network assumptions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: fuzz conflict order into `chia/wallet/wallet_rpc_api.py:get_coin_records_by_names` and assert a valid honest spend eventually processes under bounded attacker traffic
