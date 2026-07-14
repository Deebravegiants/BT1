# Q2087: request_compact_proof_of_time attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach P2P message handler `request_compact_proof_of_time` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `TimelordAPI.request_compact_proof_of_time` in `chia/timelord/timelord_api.py` executes a path where make `request_compact_proof_of_time` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/timelord/timelord_api.py:203 `TimelordAPI.request_compact_proof_of_time`
- Entrypoint: P2P message handler `request_compact_proof_of_time`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `request_compact_proof_of_time` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/timelord/timelord_api.py:request_compact_proof_of_time` and assert rewards cannot be attributed across sessions or peers
