# Q175: index cached key reuse via keychainRpc

## Question
Can an unprivileged attacker reach `keychainRpc` in `sdks/headless/src/features/keychain-rpc/index.js` through connected website RPC request that reaches key-management methods through the wallet bridge and supply crafted `port`, `port`, and `port` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: sdks/headless/src/features/keychain-rpc/index.js::keychainRpc
- Entrypoint: connected website RPC request that reaches key-management methods through the wallet bridge
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
