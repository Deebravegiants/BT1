# Q1939: transaction signer cross-account signing via TransactionSigner

## Question
Can an unprivileged attacker reach `TransactionSigner` in `features/tx-signer/src/module/transaction-signer.ts` through signTransaction request from a connected website or wallet-integrated app and supply crafted `walletAccount`, `unsignedTx`, and `txData` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Direct theft of user funds`?

## Target
- File/function: features/tx-signer/src/module/transaction-signer.ts::TransactionSigner
- Entrypoint: signTransaction request from a connected website or wallet-integrated app
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
