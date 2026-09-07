# Q3851: Nonce/salt `defaultIntentPayloadFactory` sets n tip191 a withdrawal intent 

## Question
Given that `defaultIntentPayloadFactory` sets nonce deadline = deadline + 60s, can an unprivileged party holding or predicting a `tip191` signed payload (a withdrawal intent for the user's full balance) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because a payload can be replayed in the 60s window after its `deadline` if the contract only checks the nonce deadline?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: a payload can be replayed in the 60s window after its `deadline` if the contract only checks the nonce deadline
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: Critical - a signed payload replayed or executed twice / on another contract (HackenProof: cross-chain replay, nonce management; Immunefi class: direct theft of user funds)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
