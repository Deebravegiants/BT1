# Q0392: nep413 deadline via a custom `payload` f storage_deposit

## Question
For standard `nep413` (`IntentSignerNEP413.signIntent` (also `IntentSignerNearKeypair`); `message` = JSON of {deadline, intents, signer_id}; `recipient` = verifying_contract; `nonce` base64 (32 bytes)), can an unprivileged caller alter `deadline` (the ISO timestamp after which the contract rejects the payload) via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field, given `mergeIntentPayloads` spreads `customPayload` over the base payload, so that a `storage_deposit` intent (`contract_id` = omni.bridge.near, `deposit_for_account_id`, `amount` = nativeFee) is signed and published under a `deadline` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `deadline` through via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field; the `storage_deposit` intent body
- Exploit idea: `mergeIntentPayloads` spreads `customPayload` over the base payload. For `nep413` the signed bytes are `computeSignedNep413Hash` -> `hashNEP413Message`.
- Invariant to test: signed.deadline == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `nep413` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
