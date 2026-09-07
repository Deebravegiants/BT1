# Q3660: webauthn signer_id via `sendSignedIntents(m storage_deposit

## Question
For standard `webauthn` (`makeWebAuthnMultiPayload`; `payload`, `client_data_json`, `authenticator_data`, `public_key` p256:/ed25519:), can an unprivileged caller alter `signer_id` (the account debited by intents.near) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `storage_deposit` intent (`contract_id` = omni.bridge.near, `deposit_for_account_id`, `amount` = nativeFee) is signed and published under a `signer_id` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `signer_id` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `storage_deposit` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `webauthn` the signed bytes are `computeSignedWebAuthnHash` (sha256 of payload only).
- Invariant to test: signed.signer_id == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `webauthn` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
