# Q166: index derivation scope expansion via keychainRpc

## Question
Can an unprivileged attacker reach `keychainRpc` in `sdks/headless/src/features/keychain-rpc/index.js` through connected website RPC request that reaches key-management methods through the wallet bridge and supply crafted `port`, `port`, and `port` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Direct theft of user funds`?

## Target
- File/function: sdks/headless/src/features/keychain-rpc/index.js::keychainRpc
- Entrypoint: connected website RPC request that reaches key-management methods through the wallet bridge
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
