# Q1898: new_transaction desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach P2P message handler `new_transaction` and control bundle contents that make additions, removals, and fee accounting disagree so that `CrawlerAPI.new_transaction` in `chia/seeder/crawler_api.py` executes a path where make `new_transaction` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/seeder/crawler_api.py:50 `CrawlerAPI.new_transaction`
- Entrypoint: P2P message handler `new_transaction`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `new_transaction` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/seeder/crawler_api.py:new_transaction` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
