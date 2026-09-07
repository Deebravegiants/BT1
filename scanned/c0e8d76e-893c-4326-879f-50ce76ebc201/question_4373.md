# Q4373: Nonce/salt `invalidateNonces` sets the invalida erc191 a withdrawal intent 

## Question
Given that `invalidateNonces` sets the invalidation deadline to min(now+1min, nonceDeadline), can an unprivileged party holding or predicting a `erc191` signed payload (a withdrawal intent for the user's full balance) get it executed twice, executed after the SDK user believes it invalidated, or executed on a different intents contract, because if `nonceDeadline` < now the invalidation is dead on arrival while the original (deadline = nonceDeadline - 60s) may still be live?

## Target
- File/function: packages/intents-sdk/src/intents/expirable-nonce.ts `VersionedNonceBuilder`; salt-manager.ts `SaltManager`, `StaticSaltManager`; sdk.ts `invalidateNonces`, `withSaltRetry`; intent-payload-factory.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`, `invalidateNonces`, `intentBuilder().setNonce/ setNonceRandomBytes`
- Attacker controls: nonce bytes / custom nonce, timing of calls, the salt cache state
- Exploit idea: if `nonceDeadline` < now the invalidation is dead on arrival while the original (deadline = nonceDeadline - 60s) may still be live
- Invariant to test: each signed MultiPayload executes at most once, only on `envConfig.contractID`, and never after the caller's requested invalidation.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: fake timers + mocked relay responses (INVALID_SALT / NONCE_USED / OK) and count published payloads and their nonces.
