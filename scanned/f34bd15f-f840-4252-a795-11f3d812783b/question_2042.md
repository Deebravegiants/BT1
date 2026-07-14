# Q2042: set_auto_farming attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach RPC route `set_auto_farming` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `SimulatorFullNodeRpcApi.set_auto_farming` in `chia/simulator/simulator_full_node_rpc_api.py` executes a path where make `set_auto_farming` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/simulator/simulator_full_node_rpc_api.py:52 `SimulatorFullNodeRpcApi.set_auto_farming`
- Entrypoint: RPC route `set_auto_farming`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `set_auto_farming` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/simulator/simulator_full_node_rpc_api.py:set_auto_farming` and assert rewards cannot be attributed across sessions or peers
