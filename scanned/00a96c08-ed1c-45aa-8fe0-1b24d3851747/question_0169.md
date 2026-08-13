# Q169: index cross-account signing via keychainRpc

## Question
Can an unprivileged attacker reach `keychainRpc` in `sdks/headless/src/features/keychain-rpc/index.js` through connected website RPC request that reaches key-management methods through the wallet bridge and supply crafted `port`, `port`, and `port` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Sitewide disruption of core services`?

## Target
- File/function: sdks/headless/src/features/keychain-rpc/index.js::keychainRpc
- Entrypoint: connected website RPC request that reaches key-management methods through the wallet bridge
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
