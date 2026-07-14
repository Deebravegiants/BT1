# Q3284: set_peak_block misclassifies hinted or remote coins under attacker control

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_peak_block` and control hints, remote coin metadata, and puzzle-hash attribution state so that `WalletBlockchain.set_peak_block` in `chia/wallet/wallet_blockchain.py` executes a path where make `set_peak_block` attribute a coin, hint, or remote state record to the wrong wallet or asset context, violating the invariant that hints and remote coin metadata must not remap coins to the wrong wallet or asset domain and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_blockchain.py:179 `WalletBlockchain.set_peak_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_peak_block`
- Attacker controls: hints, remote coin metadata, and puzzle-hash attribution state
- Exploit idea: make `set_peak_block` attribute a coin, hint, or remote state record to the wrong wallet or asset context
- Invariant to test: hints and remote coin metadata must not remap coins to the wrong wallet or asset domain
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz hints and remote-coin metadata through `chia/wallet/wallet_blockchain.py:set_peak_block` and assert no coin is attributed to the wrong wallet or asset
