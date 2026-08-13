# Q1711: message signer external key rebinding via signMessage

## Question
Can an unprivileged attacker reach `signMessage` in `features/message-signer/src/module/message-signer.ts` through signMessage / signIn request from a connected website and supply crafted `message`, `account`, and `walletAccount` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/message-signer/src/module/message-signer.ts::signMessage
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: fuzz derivation-path and key-identifier inputs and assert the returned key scope never exceeds the approved request
