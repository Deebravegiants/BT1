# Q1218: secp256k1 cached key reuse via createSigner

## Question
Can an unprivileged attacker reach `createSigner` in `features/keychain/module/crypto/secp256k1.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `port`, `signature`, and `seedId` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/keychain/module/crypto/secp256k1.js::createSigner
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
