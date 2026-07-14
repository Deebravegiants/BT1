# Q3989: handle_nft replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_nft` and control stale NFT singleton state replayed after ownership moved so that `WalletStateManager.handle_nft` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_nft` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1529 `WalletStateManager.handle_nft`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_nft`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `handle_nft` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/wallet/wallet_state_manager.py:handle_nft` and assert the old state cannot mutate the new owner record
