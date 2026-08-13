# Q160: index cached key reuse via keychainRpc

## Question
Can an unprivileged attacker reach `keychainRpc` in `sdks/headless/src/features/keychain-rpc/index.js` through connected website RPC request that reaches key-management methods through the wallet bridge and supply crafted `port`, `port`, and `port` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: sdks/headless/src/features/keychain-rpc/index.js::keychainRpc
- Entrypoint: connected website RPC request that reaches key-management methods through the wallet bridge
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: fuzz derivation-path and key-identifier inputs and assert the returned key scope never exceeds the approved request
