# Q2236: create_mirror_puzzle desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_mirror_puzzle` and control bundle contents that make additions, removals, and fee accounting disagree so that `create_mirror_puzzle` in `chia/wallet/db_wallet/db_wallet_puzzles.py` executes a path where make `create_mirror_puzzle` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/db_wallet/db_wallet_puzzles.py:90 `create_mirror_puzzle`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_mirror_puzzle`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `create_mirror_puzzle` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/wallet/db_wallet/db_wallet_puzzles.py:create_mirror_puzzle` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
