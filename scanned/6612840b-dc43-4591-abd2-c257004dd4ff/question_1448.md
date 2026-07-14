# Q1448: create_bundle_from_mempool desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `create_bundle_from_mempool` and control bundle contents that make additions, removals, and fee accounting disagree so that `MempoolManager.create_bundle_from_mempool` in `chia/full_node/mempool_manager.py` executes a path where make `create_bundle_from_mempool` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/mempool_manager.py:411 `MempoolManager.create_bundle_from_mempool`
- Entrypoint: full node mempool, sync, or peer flow reaching `create_bundle_from_mempool`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `create_bundle_from_mempool` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/full_node/mempool_manager.py:create_bundle_from_mempool` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
