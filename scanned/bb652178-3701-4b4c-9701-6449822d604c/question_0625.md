# Q625: farming_info attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach P2P message handler `farming_info` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `FarmerAPI.farming_info` in `chia/farmer/farmer_api.py` executes a path where make `farming_info` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/farmer/farmer_api.py:772 `FarmerAPI.farming_info`
- Entrypoint: P2P message handler `farming_info`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `farming_info` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/farmer/farmer_api.py:farming_info` and assert rewards cannot be attributed across sessions or peers
