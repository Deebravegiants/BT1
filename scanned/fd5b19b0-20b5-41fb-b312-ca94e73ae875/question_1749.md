# Q1749: create_p2_singleton_puzzle_hash desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_p2_singleton_puzzle_hash` and control bundle contents that make additions, removals, and fee accounting disagree so that `create_p2_singleton_puzzle_hash` in `chia/pools/pool_puzzles.py` executes a path where make `create_p2_singleton_puzzle_hash` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/pools/pool_puzzles.py:103 `create_p2_singleton_puzzle_hash`
- Entrypoint: pool wallet or singleton spend flow reaching `create_p2_singleton_puzzle_hash`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `create_p2_singleton_puzzle_hash` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/pools/pool_puzzles.py:create_p2_singleton_puzzle_hash` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
