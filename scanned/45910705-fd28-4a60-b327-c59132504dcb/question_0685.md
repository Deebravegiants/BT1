# Q0685: nep413 nonce via `sendSignedIntents(m token_diff

## Question
For standard `nep413` (`IntentSignerNEP413.signIntent` (also `IntentSignerNearKeypair`); `message` = JSON of {deadline, intents, signer_id}; `recipient` = verifying_contract; `nonce` base64 (32 bytes)), can an unprivileged caller alter `nonce` (the 32-byte replay guard (versioned salted nonce)) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `token_diff` intent (`diff` map from `feeEstimation.quote`, `referral`) is signed and published under a `nonce` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `nonce` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `token_diff` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `nep413` the signed bytes are `computeSignedNep413Hash` -> `hashNEP413Message`.
- Invariant to test: signed.nonce == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `nep413` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
