# Q3460: new_peak_from_untrusted misclassifies hinted or remote coins under attacker control

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak_from_untrusted` and control hints, remote coin metadata, and puzzle-hash attribution state so that `WalletNode.new_peak_from_untrusted` in `chia/wallet/wallet_node.py` executes a path where make `new_peak_from_untrusted` attribute a coin, hint, or remote state record to the wrong wallet or asset context, violating the invariant that hints and remote coin metadata must not remap coins to the wrong wallet or asset domain and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_node.py:1273 `WalletNode.new_peak_from_untrusted`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak_from_untrusted`
- Attacker controls: hints, remote coin metadata, and puzzle-hash attribution state
- Exploit idea: make `new_peak_from_untrusted` attribute a coin, hint, or remote state record to the wrong wallet or asset context
- Invariant to test: hints and remote coin metadata must not remap coins to the wrong wallet or asset domain
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz hints and remote-coin metadata through `chia/wallet/wallet_node.py:new_peak_from_untrusted` and assert no coin is attributed to the wrong wallet or asset
