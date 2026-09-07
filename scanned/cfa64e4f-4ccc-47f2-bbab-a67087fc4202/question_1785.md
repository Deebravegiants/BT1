# Q1785: tip191 signer_id via a custom `payload` f storage_deposit

## Question
For standard `tip191` (`prepareSwapSignedData` case `TRON`; `payload` string as signed by TronLink), can an unprivileged caller alter `signer_id` (the account debited by intents.near) via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field, given `mergeIntentPayloads` spreads `customPayload` over the base payload, so that a `storage_deposit` intent (`contract_id` = omni.bridge.near, `deposit_for_account_id`, `amount` = nativeFee) is signed and published under a `signer_id` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `signer_id` through via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field; the `storage_deposit` intent body
- Exploit idea: `mergeIntentPayloads` spreads `customPayload` over the base payload. For `tip191` the signed bytes are `computeSignedTip191Hash` (keccak256 of `\x19TRON Signed Message:\n<len>` + payload).
- Invariant to test: signed.signer_id == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `tip191` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
