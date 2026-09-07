# Q3378: Compose raw_ed25519: a pre-signed payload with an expired dea

## Question
With `signedIntents` composition on a `raw_ed25519` withdrawal, when a pre-signed payload with an expired deadline that the relayer rejects, failing the atomic batch after the user signed, does `composeMultiPayloads` + `publishIntents` let the user's freshly signed payload execute atomically with payloads they never inspected, and `signAndSendIntent` return `tickets[beforeCount]` as if it were the user's intent, so funds move under a different intent than the one tracked?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `composeMultiPayloads`, `signAndSendIntent` (tickets[beforeCount])
- Entrypoint: `IntentsSDK.signAndSendIntent` / `signAndSendWithdrawalIntent` with `intent.signedIntents`
- Attacker controls: `signedIntents.before[]`, `.after[]` MultiPayloads (any signer)
- Exploit idea: No validation of pre-signed payloads' `verifying_contract`, `signer_id`, `deadline` or intents; ticket index is positional.
- Invariant to test: returned intentHash == hash of the payload the user signed; every co-published payload was supplied knowingly by the same caller.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: pass crafted before/after payloads, mock `publish_intents` returning N hashes, assert returned ticket and published order.
