# Q1005: Nonce/salt `decodeNonce` reads `bytes[4]` as ve webauthn an `invalidateNonces

## Question
Given that `decodeNonce` reads `bytes[4]` as version and never validates it, can an unprivileged party holding or predicting a `webauthn` signed payload (an `invalidateNonces` empty intent) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because a nonce with version 1 decodes with the v0 borsh schema; `invalidateNonces` then computes a deadline from garbage?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: a nonce with version 1 decodes with the v0 borsh schema; `invalidateNonces` then computes a deadline from garbage
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
