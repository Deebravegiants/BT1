# Q3955: auto_claim_coins misclassifies hinted or remote coins under attacker control

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `auto_claim_coins` and control hints, remote coin metadata, and puzzle-hash attribution state so that `WalletStateManager.auto_claim_coins` in `chia/wallet/wallet_state_manager.py` executes a path where make `auto_claim_coins` attribute a coin, hint, or remote state record to the wrong wallet or asset context, violating the invariant that hints and remote coin metadata must not remap coins to the wrong wallet or asset domain and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1043 `WalletStateManager.auto_claim_coins`
- Entrypoint: wallet RPC or wallet sync flow reaching `auto_claim_coins`
- Attacker controls: hints, remote coin metadata, and puzzle-hash attribution state
- Exploit idea: make `auto_claim_coins` attribute a coin, hint, or remote state record to the wrong wallet or asset context
- Invariant to test: hints and remote coin metadata must not remap coins to the wrong wallet or asset domain
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz hints and remote-coin metadata through `chia/wallet/wallet_state_manager.py:auto_claim_coins` and assert no coin is attributed to the wrong wallet or asset
