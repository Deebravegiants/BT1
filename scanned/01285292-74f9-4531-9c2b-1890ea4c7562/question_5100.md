# Q5100: Nonce/salt `invalidateNonces` relies on relayer tip191 an `invalidateNonces

## Question
Given that `invalidateNonces` relies on relayer in-memory invalidation, never on-chain, can an unprivileged party holding or predicting a `tip191` signed payload (an `invalidateNonces` empty intent) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because a payload published directly on-chain (or via another relayer) by whoever holds it still executes?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: a payload published directly on-chain (or via another relayer) by whoever holds it still executes
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: Critical - a signed payload replayed or executed twice / on another contract (HackenProof: cross-chain replay, nonce management; Immunefi class: direct theft of user funds)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
