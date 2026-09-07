# Q2220: Nonce/salt `setNonce(nonce)` accepts any base64 webauthn an `invalidateNonces

## Question
Given that `setNonce(nonce)` accepts any base64 string including a legacy 32-byte random nonce, can an unprivileged party holding or predicting a `webauthn` signed payload (an `invalidateNonces` empty intent) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because a legacy nonce bypasses the expirable-nonce deadline coupling?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: a legacy nonce bypasses the expirable-nonce deadline coupling
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
