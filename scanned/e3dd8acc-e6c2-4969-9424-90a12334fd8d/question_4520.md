# Q4520: ton_connect signer_id via `sendSignedIntents(m transfer

## Question
For standard `ton_connect` (`prepareSwapSignedData` case `TON_CONNECT`; `address`, `domain`, `timestamp`, `payload.text`, `public_key` derived from `userAddress`), can an unprivileged caller alter `signer_id` (the account debited by intents.near) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `transfer` intent (`receiver_id`, `tokens` map, `memo` (IntentsBridge internal transfer)) is signed and published under a `signer_id` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `signer_id` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `transfer` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `ton_connect` the signed bytes are `computeTonConnectHash` (0xffff || 'ton-connect/sign-data/' || wc || addr || domain_len || domain || ts || 'txt' || len || text).
- Invariant to test: signed.signer_id == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `ton_connect` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
