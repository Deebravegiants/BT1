# Q1180: register_for_coin_updates desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach P2P message handler `register_for_coin_updates` and control bundle contents that make additions, removals, and fee accounting disagree so that `FullNodeAPI.register_for_coin_updates` in `chia/full_node/full_node_api.py` executes a path where make `register_for_coin_updates` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/full_node_api.py:1890 `FullNodeAPI.register_for_coin_updates`
- Entrypoint: P2P message handler `register_for_coin_updates`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `register_for_coin_updates` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/full_node/full_node_api.py:register_for_coin_updates` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
