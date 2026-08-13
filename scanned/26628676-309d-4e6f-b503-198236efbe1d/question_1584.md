# Q1584: cached sodium encryptor cached key reuse via createCachedSodiumEncryptor

## Question
Can an unprivileged attacker reach `createCachedSodiumEncryptor` in `features/cached-sodium-encryptor/module/cached-sodium-encryptor.ts` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `params`, `port`, and `seedId` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/cached-sodium-encryptor/module/cached-sodium-encryptor.ts::createCachedSodiumEncryptor
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
