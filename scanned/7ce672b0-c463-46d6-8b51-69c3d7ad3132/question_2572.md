# Q2572: add_pool_reward replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_pool_reward` and control stale NFT singleton state replayed after ownership moved so that `PlotNFTStore.add_pool_reward` in `chia/wallet/plotnft_wallet/plotnft_store.py` executes a path where make `add_pool_reward` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_store.py:113 `PlotNFTStore.add_pool_reward`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_pool_reward`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `add_pool_reward` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/wallet/plotnft_wallet/plotnft_store.py:add_pool_reward` and assert the old state cannot mutate the new owner record
