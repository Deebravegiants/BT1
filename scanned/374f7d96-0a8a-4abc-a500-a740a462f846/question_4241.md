# Q4241: webauthn intents via `IntentPayloadBuilde mt_withdraw

## Question
For standard `webauthn` (`makeWebAuthnMultiPayload`; `payload`, `client_data_json`, `authenticator_data`, `public_key` p256:/ed25519:), can an unprivileged caller alter `intents` (the ordered list of `IntentPrimitive`s executed atomically) via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`), given `buildWithSalt` trusts every setter and only validates `signer_id` format, so that a `mt_withdraw` intent (`token`, `receiver_id`, `token_ids`, `amounts`, `msg`, `min_gas` (HOT)) is signed and published under a `intents` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `intents` through via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`); the `mt_withdraw` intent body
- Exploit idea: `buildWithSalt` trusts every setter and only validates `signer_id` format. For `webauthn` the signed bytes are `computeSignedWebAuthnHash` (sha256 of payload only).
- Invariant to test: signed.intents == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `webauthn` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
