# Q2429: create_new_nft_wallet replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_nft_wallet` and control stale NFT singleton state replayed after ownership moved so that `NFTWallet.create_new_nft_wallet` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `create_new_nft_wallet` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:88 `NFTWallet.create_new_nft_wallet`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_nft_wallet`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `create_new_nft_wallet` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/wallet/nft_wallet/nft_wallet.py:create_new_nft_wallet` and assert the old state cannot mutate the new owner record
