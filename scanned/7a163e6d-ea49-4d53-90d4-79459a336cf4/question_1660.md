# Q1660: hardware signer derivation scope expansion via signMessage

## Question
Can an unprivileged attacker reach `signMessage` in `features/message-signer/src/module/hardware-signer.ts` through signMessage / signIn request from a connected website and supply crafted `message`, `account`, and `walletAccount` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/message-signer/src/module/hardware-signer.ts::signMessage
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
