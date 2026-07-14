# Q3984: handle_did misclassifies hinted or remote coins under attacker control

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_did` and control hints, remote coin metadata, and puzzle-hash attribution state so that `WalletStateManager.handle_did` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_did` attribute a coin, hint, or remote state record to the wrong wallet or asset context, violating the invariant that hints and remote coin metadata must not remap coins to the wrong wallet or asset domain and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1365 `WalletStateManager.handle_did`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_did`
- Attacker controls: hints, remote coin metadata, and puzzle-hash attribution state
- Exploit idea: make `handle_did` attribute a coin, hint, or remote state record to the wrong wallet or asset context
- Invariant to test: hints and remote coin metadata must not remap coins to the wrong wallet or asset domain
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz hints and remote-coin metadata through `chia/wallet/wallet_state_manager.py:handle_did` and assert no coin is attributed to the wrong wallet or asset
