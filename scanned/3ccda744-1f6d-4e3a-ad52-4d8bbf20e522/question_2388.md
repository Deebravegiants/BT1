# Q2388: create_nft_layer_puzzle_with_curry_params replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_nft_layer_puzzle_with_curry_params` and control stale NFT singleton state replayed after ownership moved so that `create_nft_layer_puzzle_with_curry_params` in `chia/wallet/nft_wallet/nft_puzzle_utils.py` executes a path where make `create_nft_layer_puzzle_with_curry_params` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_puzzle_utils.py:34 `create_nft_layer_puzzle_with_curry_params`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_nft_layer_puzzle_with_curry_params`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `create_nft_layer_puzzle_with_curry_params` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/wallet/nft_wallet/nft_puzzle_utils.py:create_nft_layer_puzzle_with_curry_params` and assert the old state cannot mutate the new owner record
