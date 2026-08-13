# Q1713: message signer cross-account signing via createMessageSigner

## Question
Can an unprivileged attacker reach `createMessageSigner` in `features/message-signer/src/module/message-signer.ts` through signMessage / signIn request from a connected website and supply crafted `walletAccount`, `name`, and `port` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Direct theft of user funds`?

## Target
- File/function: features/message-signer/src/module/message-signer.ts::createMessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
