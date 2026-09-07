# Q3255: raw_ed25519 nonce via a pre-signed `MultiP transfer

## Question
For standard `raw_ed25519` (`prepareSwapSignedData` case `SOLANA`; `payload` = UTF-8 of the message bytes; `public_key` = `ed25519:<userAddress>`), can an unprivileged caller alter `nonce` (the 32-byte replay guard (versioned salted nonce)) via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`, given composed payloads are published atomically without inspection, so that a `transfer` intent (`receiver_id`, `tokens` map, `memo` (IntentsBridge internal transfer)) is signed and published under a `nonce` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `nonce` through via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`; the `transfer` intent body
- Exploit idea: composed payloads are published atomically without inspection. For `raw_ed25519` the signed bytes are `computeSignedRawEd25519Hash` (sha256 of payload).
- Invariant to test: signed.nonce == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `raw_ed25519` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
