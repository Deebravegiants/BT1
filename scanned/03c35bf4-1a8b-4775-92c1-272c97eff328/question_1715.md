# Q1715: message signer derivation scope expansion via #normalizeWalletAccount

## Question
Can an unprivileged attacker reach `#normalizeWalletAccount` in `features/message-signer/src/module/message-signer.ts` through signMessage / signIn request from a connected website and supply crafted `port`, `message`, and `account` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/message-signer/src/module/message-signer.ts::#normalizeWalletAccount
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: fuzz derivation-path and key-identifier inputs and assert the returned key scope never exceeds the approved request
