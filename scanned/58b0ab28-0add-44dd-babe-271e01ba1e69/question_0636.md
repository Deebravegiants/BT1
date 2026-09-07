# Q0636: Intent dedupe ft_withdraw: a factory returning the base intents plu

## Question
When a factory returning the base intents plus one more, so base intents appear twice for a `ft_withdraw` intent (`token`, `receiver_id`, `amount`, `memo`/`msg`, `storage_deposit`, `min_gas`), does `mergeIntentPayloads`' `Array.from(new Set([...customPayloadIntents, ...basePayload.intents]))` produce a signed `intents` array whose length and order differ from what the caller built, so the user is debited twice or the atomic ordering the fee logic relies on is broken?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `mergeIntentPayloads`
- Entrypoint: `IntentsSDK.signAndSendIntent` with `payload` factory / `signAndSendWithdrawalIntent` with `intent.payload`
- Attacker controls: the `IntentPayloadFactory` return value and the `intents` array
- Exploit idea: `Set` dedupes by reference identity; value-equal duplicates survive, reference-equal legit repeats collapse; ordering puts custom intents first.
- Invariant to test: signed intents == caller intents, same multiset, same order.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: pass a factory that returns duplicates / reordered intents and inspect `intentPayload.intents` in `onBeforePublishIntent`.
