# Q2589: rollback_to_block redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `rollback_to_block` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `PlotNFTStore.rollback_to_block` in `chia/wallet/plotnft_wallet/plotnft_store.py` executes a path where make `rollback_to_block` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_store.py:258 `PlotNFTStore.rollback_to_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `rollback_to_block`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `rollback_to_block` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/wallet/plotnft_wallet/plotnft_store.py:rollback_to_block` with swapped payout state and assert rewards cannot redirect
