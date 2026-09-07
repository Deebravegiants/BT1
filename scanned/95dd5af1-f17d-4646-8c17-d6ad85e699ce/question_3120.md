# Q3120: raw_ed25519 deadline via `sendSignedIntents(m transfer

## Question
For standard `raw_ed25519` (`prepareSwapSignedData` case `SOLANA`; `payload` = UTF-8 of the message bytes; `public_key` = `ed25519:<userAddress>`), can an unprivileged caller alter `deadline` (the ISO timestamp after which the contract rejects the payload) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `transfer` intent (`receiver_id`, `tokens` map, `memo` (IntentsBridge internal transfer)) is signed and published under a `deadline` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `deadline` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `transfer` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `raw_ed25519` the signed bytes are `computeSignedRawEd25519Hash` (sha256 of payload).
- Invariant to test: signed.deadline == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `raw_ed25519` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
