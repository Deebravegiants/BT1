# Q3434: raw_ed25519 intents via a pre-signed `MultiP token_diff

## Question
For standard `raw_ed25519` (`prepareSwapSignedData` case `SOLANA`; `payload` = UTF-8 of the message bytes; `public_key` = `ed25519:<userAddress>`), can an unprivileged caller alter `intents` (the ordered list of `IntentPrimitive`s executed atomically) via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`, given composed payloads are published atomically without inspection, so that a `token_diff` intent (`diff` map from `feeEstimation.quote`, `referral`) is signed and published under a `intents` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `intents` through via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`; the `token_diff` intent body
- Exploit idea: composed payloads are published atomically without inspection. For `raw_ed25519` the signed bytes are `computeSignedRawEd25519Hash` (sha256 of payload).
- Invariant to test: signed.intents == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `raw_ed25519` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
