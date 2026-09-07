# Q0965: erc191 signer_id via a pre-signed `MultiP ft_withdraw

## Question
For standard `erc191` (`IntentSignerViem.signIntent`; `payload` = JSON of {signer_id, verifying_contract, deadline, nonce, intents}), can an unprivileged caller alter `signer_id` (the account debited by intents.near) via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`, given composed payloads are published atomically without inspection, so that a `ft_withdraw` intent (`token`, `receiver_id`, `amount`, `memo`/`msg`, `storage_deposit`, `min_gas`) is signed and published under a `signer_id` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `signer_id` through via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`; the `ft_withdraw` intent body
- Exploit idea: composed payloads are published atomically without inspection. For `erc191` the signed bytes are `computeSignedErc191Hash` (keccak256 of `\x19Ethereum Signed Message:\n<len>` + payload).
- Invariant to test: signed.signer_id == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: use a `erc191` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
