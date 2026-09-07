# Q2615: tip191 intents via `sendSignedIntents(m storage_deposit

## Question
For standard `tip191` (`prepareSwapSignedData` case `TRON`; `payload` string as signed by TronLink), can an unprivileged caller alter `intents` (the ordered list of `IntentPrimitive`s executed atomically) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `storage_deposit` intent (`contract_id` = omni.bridge.near, `deposit_for_account_id`, `amount` = nativeFee) is signed and published under a `intents` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `intents` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `storage_deposit` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `tip191` the signed bytes are `computeSignedTip191Hash` (keccak256 of `\x19TRON Signed Message:\n<len>` + payload).
- Invariant to test: signed.intents == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `tip191` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
