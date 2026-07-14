# Q1652: remove_plot_directory attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach RPC route `remove_plot_directory` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `HarvesterRpcApi.remove_plot_directory` in `chia/harvester/harvester_rpc_api.py` executes a path where make `remove_plot_directory` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/harvester/harvester_rpc_api.py:85 `HarvesterRpcApi.remove_plot_directory`
- Entrypoint: RPC route `remove_plot_directory`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `remove_plot_directory` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/harvester/harvester_rpc_api.py:remove_plot_directory` and assert rewards cannot be attributed across sessions or peers
