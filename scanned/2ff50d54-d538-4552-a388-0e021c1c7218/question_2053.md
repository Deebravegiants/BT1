# Q2053: new_peak_timelord attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach P2P message handler `new_peak_timelord` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `TimelordAPI.new_peak_timelord` in `chia/timelord/timelord_api.py` executes a path where make `new_peak_timelord` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/timelord/timelord_api.py:60 `TimelordAPI.new_peak_timelord`
- Entrypoint: P2P message handler `new_peak_timelord`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `new_peak_timelord` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/timelord/timelord_api.py:new_peak_timelord` and assert rewards cannot be attributed across sessions or peers
