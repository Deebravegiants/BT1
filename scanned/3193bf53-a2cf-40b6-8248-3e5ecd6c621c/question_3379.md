# Q3379: delete_nft_by_nft_id replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `delete_nft_by_nft_id` and control stale NFT singleton state replayed after ownership moved so that `WalletNftStore.delete_nft_by_nft_id` in `chia/wallet/wallet_nft_store.py` executes a path where make `delete_nft_by_nft_id` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_nft_store.py:76 `WalletNftStore.delete_nft_by_nft_id`
- Entrypoint: wallet RPC or wallet sync flow reaching `delete_nft_by_nft_id`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `delete_nft_by_nft_id` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/wallet/wallet_nft_store.py:delete_nft_by_nft_id` and assert the old state cannot mutate the new owner record
