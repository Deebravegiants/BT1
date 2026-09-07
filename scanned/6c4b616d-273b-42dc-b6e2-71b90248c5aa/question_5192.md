# Q5192: ton_connect intents via `sendSignedIntents(m ft_withdraw

## Question
For standard `ton_connect` (`prepareSwapSignedData` case `TON_CONNECT`; `address`, `domain`, `timestamp`, `payload.text`, `public_key` derived from `userAddress`), can an unprivileged caller alter `intents` (the ordered list of `IntentPrimitive`s executed atomically) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `ft_withdraw` intent (`token`, `receiver_id`, `amount`, `memo`/`msg`, `storage_deposit`, `min_gas`) is signed and published under a `intents` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `intents` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `ft_withdraw` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `ton_connect` the signed bytes are `computeTonConnectHash` (0xffff || 'ton-connect/sign-data/' || wc || addr || domain_len || domain || ts || 'txt' || len || text).
- Invariant to test: signed.intents == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `ton_connect` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
