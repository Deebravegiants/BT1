# Q1085: cardano external key rebinding via seedToCardanoV1Seed

## Question
Can an unprivileged attacker reach `seedToCardanoV1Seed` in `features/keychain/module/crypto/cardano.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `port`, `message`, and `signature` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/keychain/module/crypto/cardano.js::seedToCardanoV1Seed
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: fuzz derivation-path and key-identifier inputs and assert the returned key scope never exceeds the approved request
