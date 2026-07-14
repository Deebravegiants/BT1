# Q2595: claim_rewards replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `claim_rewards` and control stale NFT singleton state replayed after ownership moved so that `PlotNFT2Wallet.claim_rewards` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `claim_rewards` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:137 `PlotNFT2Wallet.claim_rewards`
- Entrypoint: wallet RPC or wallet sync flow reaching `claim_rewards`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `claim_rewards` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/wallet/plotnft_wallet/plotnft_wallet.py:claim_rewards` and assert the old state cannot mutate the new owner record
