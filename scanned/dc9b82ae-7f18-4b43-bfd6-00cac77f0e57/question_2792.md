# Q2792: raw_ed25519 verifying_contract via a custom `payload` f ft_withdraw

## Question
For standard `raw_ed25519` (`prepareSwapSignedData` case `SOLANA`; `payload` = UTF-8 of the message bytes; `public_key` = `ed25519:<userAddress>`), can an unprivileged caller alter `verifying_contract` (the contract the signature is valid for) via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field, given `mergeIntentPayloads` spreads `customPayload` over the base payload, so that a `ft_withdraw` intent (`token`, `receiver_id`, `amount`, `memo`/`msg`, `storage_deposit`, `min_gas`) is signed and published under a `verifying_contract` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `verifying_contract` through via a custom `payload` factory (`SignAndSendArgs.payload`) returning an override for this field; the `ft_withdraw` intent body
- Exploit idea: `mergeIntentPayloads` spreads `customPayload` over the base payload. For `raw_ed25519` the signed bytes are `computeSignedRawEd25519Hash` (sha256 of payload).
- Invariant to test: signed.verifying_contract == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `raw_ed25519` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
