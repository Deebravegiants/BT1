# Q1709: message signer cached key reuse via #getMessageSigner

## Question
Can an unprivileged attacker reach `#getMessageSigner` in `features/message-signer/src/module/message-signer.ts` through signMessage / signIn request from a connected website and supply crafted `name`, `port`, and `message` values that bind externally provided or freshly imported key material to an existing trusted account context, violating the invariant that signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload, and causing `Direct theft of user funds`?

## Target
- File/function: features/message-signer/src/module/message-signer.ts::#getMessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: a crafted unsigned transaction or message plus repeated signing attempts across account changes
- Exploit idea: bind externally provided or freshly imported key material to an existing trusted account context
- Invariant to test: signing and export paths must stay bound to the selected wallet account, seed, and exact approved payload
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
