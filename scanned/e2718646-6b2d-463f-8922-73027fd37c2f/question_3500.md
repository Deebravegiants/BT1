# Q3500: new_peak_wallet misclassifies hinted or remote coins under attacker control

## Question
Can an unprivileged attacker reach P2P message handler `new_peak_wallet` and control hints, remote coin metadata, and puzzle-hash attribution state so that `WalletNodeAPI.new_peak_wallet` in `chia/wallet/wallet_node_api.py` executes a path where make `new_peak_wallet` attribute a coin, hint, or remote state record to the wrong wallet or asset context, violating the invariant that hints and remote coin metadata must not remap coins to the wrong wallet or asset domain and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_node_api.py:53 `WalletNodeAPI.new_peak_wallet`
- Entrypoint: P2P message handler `new_peak_wallet`
- Attacker controls: hints, remote coin metadata, and puzzle-hash attribution state
- Exploit idea: make `new_peak_wallet` attribute a coin, hint, or remote state record to the wrong wallet or asset context
- Invariant to test: hints and remote coin metadata must not remap coins to the wrong wallet or asset domain
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz hints and remote-coin metadata through `chia/wallet/wallet_node_api.py:new_peak_wallet` and assert no coin is attributed to the wrong wallet or asset
