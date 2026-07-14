# Q2532: set_bulk_nft_did replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_bulk_nft_did` and control stale NFT singleton state replayed after ownership moved so that `NFTWallet.set_bulk_nft_did` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `set_bulk_nft_did` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:1019 `NFTWallet.set_bulk_nft_did`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_bulk_nft_did`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `set_bulk_nft_did` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/wallet/nft_wallet/nft_wallet.py:set_bulk_nft_did` and assert the old state cannot mutate the new owner record
