# Q1634: errors cached key reuse via UnsupportedWalletAccountSource

## Question
Can an unprivileged attacker reach `UnsupportedWalletAccountSource` in `features/message-signer/src/module/errors.ts` through signMessage / signIn request from a connected website and supply crafted `port`, `account`, and `port` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/message-signer/src/module/errors.ts::UnsupportedWalletAccountSource
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
