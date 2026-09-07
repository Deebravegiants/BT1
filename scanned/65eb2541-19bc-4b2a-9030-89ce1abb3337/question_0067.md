# Q0067: nep413 signer_id via `IntentPayloadBuilde transfer

## Question
For standard `nep413` (`IntentSignerNEP413.signIntent` (also `IntentSignerNearKeypair`); `message` = JSON of {deadline, intents, signer_id}; `recipient` = verifying_contract; `nonce` base64 (32 bytes)), can an unprivileged caller alter `signer_id` (the account debited by intents.near) via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`), given `buildWithSalt` trusts every setter and only validates `signer_id` format, so that a `transfer` intent (`receiver_id`, `tokens` map, `memo` (IntentsBridge internal transfer)) is signed and published under a `signer_id` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `signer_id` through via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`); the `transfer` intent body
- Exploit idea: `buildWithSalt` trusts every setter and only validates `signer_id` format. For `nep413` the signed bytes are `computeSignedNep413Hash` -> `hashNEP413Message`.
- Invariant to test: signed.signer_id == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `nep413` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
