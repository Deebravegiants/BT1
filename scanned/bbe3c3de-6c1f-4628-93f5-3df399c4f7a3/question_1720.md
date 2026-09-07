# Q1720: erc191 intents via `sendSignedIntents(m native_withdraw

## Question
For standard `erc191` (`IntentSignerViem.signIntent`; `payload` = JSON of {signer_id, verifying_contract, deadline, nonce, intents}), can an unprivileged caller alter `intents` (the ordered list of `IntentPrimitive`s executed atomically) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `native_withdraw` intent (`receiver_id`, `amount` (Direct route for `wrap.near` without `msg`)) is signed and published under a `intents` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `intents` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `native_withdraw` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `erc191` the signed bytes are `computeSignedErc191Hash` (keccak256 of `\x19Ethereum Signed Message:\n<len>` + payload).
- Invariant to test: signed.intents == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `erc191` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
