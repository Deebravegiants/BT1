# Q104: validated_signature reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `validated_signature` and control one request's authorization context plus a second request that reuses cached state so that `PreValidationResult.validated_signature` in `chia/consensus/multiprocess_validation.py` executes a path where make `validated_signature` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/consensus/multiprocess_validation.py:54 `PreValidationResult.validated_signature`
- Entrypoint: peer-supplied block, proof, or spend path reaching `validated_signature`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `validated_signature` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/consensus/multiprocess_validation.py:validated_signature` with different identities and assert auth state cannot bleed across them
