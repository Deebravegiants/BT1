# Q1640: request_plots attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach P2P message handler `request_plots` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `HarvesterAPI.request_plots` in `chia/harvester/harvester_api.py` executes a path where make `request_plots` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/harvester/harvester_api.py:529 `HarvesterAPI.request_plots`
- Entrypoint: P2P message handler `request_plots`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `request_plots` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/harvester/harvester_api.py:request_plots` and assert rewards cannot be attributed across sessions or peers
