# Q833: signage_point_post_processing attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `signage_point_post_processing` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `FullNode.signage_point_post_processing` in `chia/full_node/full_node.py` executes a path where make `signage_point_post_processing` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/full_node.py:1847 `FullNode.signage_point_post_processing`
- Entrypoint: full node mempool, sync, or peer flow reaching `signage_point_post_processing`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `signage_point_post_processing` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/full_node/full_node.py:signage_point_post_processing` and assert rewards cannot be attributed across sessions or peers
