# Q5450: sep53 verifying_contract via `IntentPayloadBuilde ft_withdraw

## Question
For standard `sep53` (`prepareSwapSignedData` case `STELLAR_SEP53`; `payload`, `public_key` = base58 of `stellarAddressToBytes(userAddress)`), can an unprivileged caller alter `verifying_contract` (the contract the signature is valid for) via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`), given `buildWithSalt` trusts every setter and only validates `signer_id` format, so that a `ft_withdraw` intent (`token`, `receiver_id`, `amount`, `memo`/`msg`, `storage_deposit`, `min_gas`) is signed and published under a `verifying_contract` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `verifying_contract` through via `IntentPayloadBuilder` setters (`setSigner`, `setDeadline`, `setNonce`, `setVerifyingContract`, `addIntents`); the `ft_withdraw` intent body
- Exploit idea: `buildWithSalt` trusts every setter and only validates `signer_id` format. For `sep53` the signed bytes are `computeSignedSep53Hash` (sha256 of 'Stellar Signed Message:\n' + payload).
- Invariant to test: signed.verifying_contract == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `sep53` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
