# Q103: validated_signature applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `validated_signature` and control public RPC or WebSocket command arguments that select protected actions so that `PreValidationResult.validated_signature` in `chia/consensus/multiprocess_validation.py` executes a path where reach a privileged path in `validated_signature` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/consensus/multiprocess_validation.py:54 `PreValidationResult.validated_signature`
- Entrypoint: peer-supplied block, proof, or spend path reaching `validated_signature`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `validated_signature` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/consensus/multiprocess_validation.py:validated_signature` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
