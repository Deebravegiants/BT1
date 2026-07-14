# Q1776: create_absorb_spend redirects pool rewards or singleton transitions

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_absorb_spend` and control pool singleton state, payout instructions, reward claims, and absorb timing so that `create_absorb_spend` in `chia/pools/pool_puzzles.py` executes a path where make `create_absorb_spend` redirect pool rewards or singleton state transitions away from the rightful owner, violating the invariant that pool reward claims and singleton transitions must only benefit the rightful singleton owner and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/pools/pool_puzzles.py:252 `create_absorb_spend`
- Entrypoint: pool wallet or singleton spend flow reaching `create_absorb_spend`
- Attacker controls: pool singleton state, payout instructions, reward claims, and absorb timing
- Exploit idea: make `create_absorb_spend` redirect pool rewards or singleton state transitions away from the rightful owner
- Invariant to test: pool reward claims and singleton transitions must only benefit the rightful singleton owner
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: simulate absorb or claim flows in `chia/pools/pool_puzzles.py:create_absorb_spend` with swapped payout state and assert rewards cannot redirect
