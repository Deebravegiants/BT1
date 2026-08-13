# Q200: index cached key reuse via cachedSodiumEncryptorRpc

## Question
Can an unprivileged attacker reach `cachedSodiumEncryptorRpc` in `sdks/headless/src/features/cached-sodium-encryptor-rpc/index.js` through wallet RPC call that asks the SDK to decrypt or unlock persisted wallet material and supply crafted `port`, `port`, and `port` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Sitewide disruption of core services`?

## Target
- File/function: sdks/headless/src/features/cached-sodium-encryptor-rpc/index.js::cachedSodiumEncryptorRpc
- Entrypoint: wallet RPC call that asks the SDK to decrypt or unlock persisted wallet material
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
