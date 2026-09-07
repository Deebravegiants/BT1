# Q1265: Nonce/salt `encodeNonce` accepts a caller `rand nep413 an `invalidateNonces

## Question
Given that `encodeNonce` accepts a caller `randomBytes` of exactly 15 bytes with no entropy check, can an unprivileged party holding or predicting a `nep413` signed payload (an `invalidateNonces` empty intent) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because an integrator deriving nonce bytes from user-controlled data lets a counterparty predict/replay nonces?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: an integrator deriving nonce bytes from user-controlled data lets a counterparty predict/replay nonces
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: Critical - a signed payload replayed or executed twice / on another contract (HackenProof: cross-chain replay, nonce management; Immunefi class: direct theft of user funds)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
