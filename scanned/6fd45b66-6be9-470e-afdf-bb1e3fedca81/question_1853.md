# Q1853: seed signer derivation scope expansion via signTransaction

## Question
Can an unprivileged attacker reach `signTransaction` in `features/tx-signer/src/module/seed-signer.ts` through signTransaction request from a connected website or wallet-integrated app and supply crafted `txMeta`, `name`, and `port` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/tx-signer/src/module/seed-signer.ts::signTransaction
- Entrypoint: signTransaction request from a connected website or wallet-integrated app
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
