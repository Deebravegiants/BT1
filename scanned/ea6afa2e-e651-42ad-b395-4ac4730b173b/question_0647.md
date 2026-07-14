# Q647: set_reward_targets attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach RPC route `set_reward_targets` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `FarmerRpcApi.set_reward_targets` in `chia/farmer/farmer_rpc_api.py` executes a path where make `set_reward_targets` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/farmer/farmer_rpc_api.py:291 `FarmerRpcApi.set_reward_targets`
- Entrypoint: RPC route `set_reward_targets`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `set_reward_targets` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/farmer/farmer_rpc_api.py:set_reward_targets` and assert rewards cannot be attributed across sessions or peers
