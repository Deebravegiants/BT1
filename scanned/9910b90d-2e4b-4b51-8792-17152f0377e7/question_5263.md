# Q5263: sep53 signer_id via a custom `payload` f token_diff

## Question
For standard `sep53` (`prepareSwapSignedData` case `STELLAR_SEP53`; `payload`, `public_key` = base58 of `stellarAddressToBytes(userAddress)`), can an unprivileged caller alter `signer_id` (the account debited by intents.near) via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field, given `mergeIntentPayloads` spreads `customPayload` over the base payload, so that a `token_diff` intent (`diff` map from `feeEstimation.quote`, `referral`) is signed and published under a `signer_id` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `signer_id` through via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field; the `token_diff` intent body
- Exploit idea: `mergeIntentPayloads` spreads `customPayload` over the base payload. For `sep53` the signed bytes are `computeSignedSep53Hash` (sha256 of 'Stellar Signed Message:\n' + payload).
- Invariant to test: signed.signer_id == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `sep53` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
