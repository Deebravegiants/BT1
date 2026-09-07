# Q3240: Nonce/salt `SaltManager.getCachedSalt` serves a tip191 a withdrawal intent 

## Question
Given that `SaltManager.getCachedSalt` serves a 5-minute-old salt after the contract rotated it, can an unprivileged party holding or predicting a `tip191` signed payload (a withdrawal intent for the user's full balance) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because `withSaltRetry` re-signs a second payload with a new nonce after the first was rejected - both signed payloads now exist?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: `withSaltRetry` re-signs a second payload with a new nonce after the first was rejected - both signed payloads now exist
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: Critical - a signed payload replayed or executed twice / on another contract (HackenProof: cross-chain replay, nonce management; Immunefi class: direct theft of user funds)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
