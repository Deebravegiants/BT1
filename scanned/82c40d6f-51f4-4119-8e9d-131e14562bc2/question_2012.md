# Q2012: tip191 verifying_contract via a pre-signed `MultiP ft_withdraw

## Question
For standard `tip191` (`prepareSwapSignedData` case `TRON`; `payload` string as signed by TronLink), can an unprivileged caller alter `verifying_contract` (the contract the signature is valid for) via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`, given composed payloads are published atomically without inspection, so that a `ft_withdraw` intent (`token`, `receiver_id`, `amount`, `memo`/`msg`, `storage_deposit`, `min_gas`) is signed and published under a `verifying_contract` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `verifying_contract` through via a pre-signed `MultiPayload` passed in `signedIntents.before` / `.after`; the `ft_withdraw` intent body
- Exploit idea: composed payloads are published atomically without inspection. For `tip191` the signed bytes are `computeSignedTip191Hash` (keccak256 of `\x19TRON Signed Message:\n<len>` + payload).
- Invariant to test: signed.verifying_contract == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `tip191` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
