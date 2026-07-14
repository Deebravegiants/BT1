# Q3763: get_coin_records_by_names accepts a spend path that diverges between validation stages

## Question
Can an unprivileged attacker reach RPC route `get_coin_records_by_names` and control conflicting spend bundle fields, CLVM conditions, announcements, and fee/cost edge cases so that `WalletRpcApi.get_coin_records_by_names` in `chia/wallet/wallet_rpc_api.py` executes a path where drive `get_coin_records_by_names` through two validation paths that should be equivalent, but make one path accept a spend bundle the other path rejects, violating the invariant that mempool admission, block validation, and wallet accounting must agree on whether the same spend is valid and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1753 `WalletRpcApi.get_coin_records_by_names`
- Entrypoint: RPC route `get_coin_records_by_names`
- Attacker controls: conflicting spend bundle fields, CLVM conditions, announcements, and fee/cost edge cases
- Exploit idea: drive `get_coin_records_by_names` through two validation paths that should be equivalent, but make one path accept a spend bundle the other path rejects
- Invariant to test: mempool admission, block validation, and wallet accounting must agree on whether the same spend is valid
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: unit-test `chia/wallet/wallet_rpc_api.py:get_coin_records_by_names` with paired spend bundles that differ only in one edge-condition and assert mempool acceptance equals block acceptance
