# Q1771: seed signer external key rebinding via SeedBasedMessageSigner

## Question
Can an unprivileged attacker reach `SeedBasedMessageSigner` in `features/message-signer/src/module/seed-signer.ts` through signMessage / signIn request from a connected website and supply crafted `message`, `signature`, and `account` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/message-signer/src/module/seed-signer.ts::SeedBasedMessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: fuzz derivation-path and key-identifier inputs and assert the returned key scope never exceeds the approved request
