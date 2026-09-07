# Q0628: nep413 nonce via a pre-signed `MultiP native_withdraw

## Question
For standard `nep413` (`IntentSignerNEP413.signIntent` (also `IntentSignerNearKeypair`); `message` = JSON of {deadline, intents, signer_id}; `recipient` = verifying_contract; `nonce` base64 (32 bytes)), can an unprivileged caller alter `nonce` (the 32-byte replay guard (versioned salted nonce)) via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`, given composed payloads are published atomically without inspection, so that a `native_withdraw` intent (`receiver_id`, `amount` (Direct route for `wrap.near` without `msg`)) is signed and published under a `nonce` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `nonce` through via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`; the `native_withdraw` intent body
- Exploit idea: composed payloads are published atomically without inspection. For `nep413` the signed bytes are `computeSignedNep413Hash` -> `hashNEP413Message`.
- Invariant to test: signed.nonce == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `nep413` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
