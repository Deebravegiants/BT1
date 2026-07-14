# Q2547: mint_from_did accepts a DID recovery or transfer path with attacker-controlled lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `mint_from_did` and control backup, recovery, transfer, and parent-lineage inputs so that `NFTWallet.mint_from_did` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `mint_from_did` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority, violating the invariant that DID recovery and transfer authority must derive from the live singleton lineage only and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:1121 `NFTWallet.mint_from_did`
- Entrypoint: wallet RPC or wallet sync flow reaching `mint_from_did`
- Attacker controls: backup, recovery, transfer, and parent-lineage inputs
- Exploit idea: make `mint_from_did` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority
- Invariant to test: DID recovery and transfer authority must derive from the live singleton lineage only
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: replay attacker-crafted DID backup or recovery material into `chia/wallet/nft_wallet/nft_wallet.py:mint_from_did` and assert recovery fails without live authority
