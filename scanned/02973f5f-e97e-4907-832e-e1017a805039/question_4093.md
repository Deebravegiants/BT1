# Q4093: webauthn nonce via `IntentPayloadBuilde storage_deposit

## Question
For standard `webauthn` (`makeWebAuthnMultiPayload`; `payload`, `client_data_json`, `authenticator_data`, `public_key` p256:/ed25519:), can an unprivileged caller alter `nonce` (the 32-byte replay guard (versioned salted nonce)) via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`), given `buildWithSalt` trusts every setter and only validates `signer_id` format, so that a `storage_deposit` intent (`contract_id` = omni.bridge.near, `deposit_for_account_id`, `amount` = nativeFee) is signed and published under a `nonce` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `nonce` through via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`); the `storage_deposit` intent body
- Exploit idea: `buildWithSalt` trusts every setter and only validates `signer_id` format. For `webauthn` the signed bytes are `computeSignedWebAuthnHash` (sha256 of payload only).
- Invariant to test: signed.nonce == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `webauthn` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
