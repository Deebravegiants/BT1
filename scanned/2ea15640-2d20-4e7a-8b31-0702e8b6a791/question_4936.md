# Q4936: ton_connect nonce via `IntentPayloadBuilde mt_withdraw

## Question
For standard `ton_connect` (`prepareSwapSignedData` case `TON_CONNECT`; `address`, `domain`, `timestamp`, `payload.text`, `public_key` derived from `userAddress`), can an unprivileged caller alter `nonce` (the 32-byte replay guard (versioned salted nonce)) via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`), given `buildWithSalt` trusts every setter and only validates `signer_id` format, so that a `mt_withdraw` intent (`token`, `receiver_id`, `token_ids`, `amounts`, `msg`, `min_gas` (HOT)) is signed and published under a `nonce` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `nonce` through via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`); the `mt_withdraw` intent body
- Exploit idea: `buildWithSalt` trusts every setter and only validates `signer_id` format. For `ton_connect` the signed bytes are `computeTonConnectHash` (0xffff || 'ton-connect/sign-data/' || wc || addr || domain_len || domain || ts || 'txt' || len || text).
- Invariant to test: signed.nonce == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `ton_connect` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
