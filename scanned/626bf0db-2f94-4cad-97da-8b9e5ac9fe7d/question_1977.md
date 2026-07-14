# Q1977: request_signage_point_or_end_of_sub_slot attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach P2P message handler `request_signage_point_or_end_of_sub_slot` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `CrawlerAPI.request_signage_point_or_end_of_sub_slot` in `chia/seeder/crawler_api.py` executes a path where make `request_signage_point_or_end_of_sub_slot` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/seeder/crawler_api.py:98 `CrawlerAPI.request_signage_point_or_end_of_sub_slot`
- Entrypoint: P2P message handler `request_signage_point_or_end_of_sub_slot`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `request_signage_point_or_end_of_sub_slot` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/seeder/crawler_api.py:request_signage_point_or_end_of_sub_slot` and assert rewards cannot be attributed across sessions or peers
