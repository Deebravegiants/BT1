# Q1624: errors cached key reuse via UnsupportedWalletAccountSource

## Question
Can an unprivileged attacker reach `UnsupportedWalletAccountSource` in `features/message-signer/src/module/errors.ts` through signMessage / signIn request from a connected website and supply crafted `port`, `account`, and `port` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/message-signer/src/module/errors.ts::UnsupportedWalletAccountSource
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
