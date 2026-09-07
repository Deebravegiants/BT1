# Q4041: webauthn nonce via a custom `payload` f transfer

## Question
For standard `webauthn` (`makeWebAuthnMultiPayload`; `payload`, `client_data_json`, `authenticator_data`, `public_key` p256:/ed25519:), can an unprivileged caller alter `nonce` (the 32-byte replay guard (versioned salted nonce)) via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field, given `mergeIntentPayloads` spreads `customPayload` over the base payload, so that a `transfer` intent (`receiver_id`, `tokens` map, `memo` (IntentsBridge internal transfer)) is signed and published under a `nonce` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `nonce` through via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field; the `transfer` intent body
- Exploit idea: `mergeIntentPayloads` spreads `customPayload` over the base payload. For `webauthn` the signed bytes are `computeSignedWebAuthnHash` (sha256 of payload only).
- Invariant to test: signed.nonce == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `webauthn` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
