# Q5934: sep53 intents via a custom `payload` f ft_withdraw

## Question
For standard `sep53` (`prepareSwapSignedData` case `STELLAR_SEP53`; `payload`, `public_key` = base58 of `stellarAddressToBytes(userAddress)`), can an unprivileged caller alter `intents` (the ordered list of `IntentPrimitive`s executed atomically) via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field, given `mergeIntentPayloads` spreads `customPayload` over the base payload, so that a `ft_withdraw` intent (`token`, `receiver_id`, `amount`, `memo`/`msg`, `storage_deposit`, `min_gas`) is signed and published under a `intents` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `intents` through via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field; the `ft_withdraw` intent body
- Exploit idea: `mergeIntentPayloads` spreads `customPayload` over the base payload. For `sep53` the signed bytes are `computeSignedSep53Hash` (sha256 of 'Stellar Signed Message:\n' + payload).
- Invariant to test: signed.intents == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `sep53` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
