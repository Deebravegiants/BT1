# Q0900: erc191 signer_id via a custom `payload` f transfer

## Question
For standard `erc191` (`IntentSignerViem.signIntent`; `payload` = JSON of {signer_id, verifying_contract, deadline, nonce, intents}), can an unprivileged caller alter `signer_id` (the account debited by intents.near) via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field, given `mergeIntentPayloads` spreads `customPayload` over the base payload, so that a `transfer` intent (`receiver_id`, `tokens` map, `memo` (IntentsBridge internal transfer)) is signed and published under a `signer_id` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `signer_id` through via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field; the `transfer` intent body
- Exploit idea: `mergeIntentPayloads` spreads `customPayload` over the base payload. For `erc191` the signed bytes are `computeSignedErc191Hash` (keccak256 of `\x19Ethereum Signed Message:\n<len>` + payload).
- Invariant to test: signed.signer_id == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `erc191` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
