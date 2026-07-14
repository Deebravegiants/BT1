# Q779: new_mempool_tx desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_mempool_tx` and control bundle contents that make additions, removals, and fee accounting disagree so that `FeeStat.new_mempool_tx` in `chia/full_node/fee_tracker.py` executes a path where make `new_mempool_tx` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/fee_tracker.py:162 `FeeStat.new_mempool_tx`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_mempool_tx`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `new_mempool_tx` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/full_node/fee_tracker.py:new_mempool_tx` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
