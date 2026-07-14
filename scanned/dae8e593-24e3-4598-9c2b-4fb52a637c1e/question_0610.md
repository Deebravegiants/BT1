# Q610: new_signage_point attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach P2P message handler `new_signage_point` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `FarmerAPI.new_signage_point` in `chia/farmer/farmer_api.py` executes a path where make `new_signage_point` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/farmer/farmer_api.py:621 `FarmerAPI.new_signage_point`
- Entrypoint: P2P message handler `new_signage_point`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `new_signage_point` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/farmer/farmer_api.py:new_signage_point` and assert rewards cannot be attributed across sessions or peers
