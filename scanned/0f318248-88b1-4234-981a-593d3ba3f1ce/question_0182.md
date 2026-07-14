# Q182: start_plotting attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `start_plotting` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `WebSocketServer.start_plotting` in `chia/daemon/server.py` executes a path where make `start_plotting` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/daemon/server.py:1158 `WebSocketServer.start_plotting`
- Entrypoint: daemon WebSocket command path reaching `start_plotting`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `start_plotting` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/daemon/server.py:start_plotting` and assert rewards cannot be attributed across sessions or peers
