# Q3986: webauthn deadline via `sendSignedIntents(m native_withdraw

## Question
For standard `webauthn` (`makeWebAuthnMultiPayload`; `payload`, `client_data_json`, `authenticator_data`, `public_key` p256:/ed25519:), can an unprivileged caller alter `deadline` (the ISO timestamp after which the contract rejects the payload) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `native_withdraw` intent (`receiver_id`, `amount` (Direct route for `wrap.near` without `msg`)) is signed and published under a `deadline` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `deadline` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `native_withdraw` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `webauthn` the signed bytes are `computeSignedWebAuthnHash` (sha256 of payload only).
- Invariant to test: signed.deadline == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `webauthn` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
