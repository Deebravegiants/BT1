# Q2518: Nonce/salt `StaticSaltManager` / `EnvConfig.con nep413 a batch of 400 nonce

## Question
Given that `StaticSaltManager` / `EnvConfig.contractSalt` on a custom env, can an unprivileged party holding or predicting a `nep413` signed payload (a batch of 400 nonces created ahead of time by an integrator) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because signing for `intents.near` with a salt of another deployment yields INVALID_SALT loop or acceptance on the other contract?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: signing for `intents.near` with a salt of another deployment yields INVALID_SALT loop or acceptance on the other contract
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
