# Q2542: set_nft_did accepts stale DID lineage in a live authority path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_nft_did` and control stale DID parent or lineage state replayed into a live DID path so that `NFTWallet.set_nft_did` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `set_nft_did` accept stale DID lineage or parent state during a live authority transition, violating the invariant that stale DID parent or lineage state must not authorize live DID actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:1090 `NFTWallet.set_nft_did`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_nft_did`
- Attacker controls: stale DID parent or lineage state replayed into a live DID path
- Exploit idea: make `set_nft_did` accept stale DID lineage or parent state during a live authority transition
- Invariant to test: stale DID parent or lineage state must not authorize live DID actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: feed stale parent or lineage data into `chia/wallet/nft_wallet/nft_wallet.py:set_nft_did` during a live DID update and assert no authority bypass occurs
