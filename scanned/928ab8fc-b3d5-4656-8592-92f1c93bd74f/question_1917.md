# Q1917: seed signer cached key reuse via sign

## Question
Can an unprivileged attacker reach `sign` in `features/tx-signer/src/module/seed-signer.ts` through signTransaction request from a connected website or wallet-integrated app and supply crafted `name`, `port`, and `signature` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/tx-signer/src/module/seed-signer.ts::sign
- Entrypoint: signTransaction request from a connected website or wallet-integrated app
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
