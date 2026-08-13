# Q205: index cached key reuse via cachedSodiumEncryptorRpc

## Question
Can an unprivileged attacker reach `cachedSodiumEncryptorRpc` in `sdks/headless/src/features/cached-sodium-encryptor-rpc/index.js` through wallet RPC call that asks the SDK to decrypt or unlock persisted wallet material and supply crafted `port`, `port`, and `port` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Direct theft of user funds`?

## Target
- File/function: sdks/headless/src/features/cached-sodium-encryptor-rpc/index.js::cachedSodiumEncryptorRpc
- Entrypoint: wallet RPC call that asks the SDK to decrypt or unlock persisted wallet material
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
