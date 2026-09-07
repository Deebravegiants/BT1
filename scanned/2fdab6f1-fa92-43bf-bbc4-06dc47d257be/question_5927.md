# Q5927: sep53 nonce via `sendSignedIntents(m storage_deposit

## Question
For standard `sep53` (`prepareSwapSignedData` case `STELLAR_SEP53`; `payload`, `public_key` = base58 of `stellarAddressToBytes(userAddress)`), can an unprivileged caller alter `nonce` (the 32-byte replay guard (versioned salted nonce)) via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere, given the SDK only forwards; no check that fields match `envConfig`, so that a `storage_deposit` intent (`contract_id` = omni.bridge.near, `deposit_for_account_id`, `amount` = nativeFee) is signed and published under a `nonce` the SDK user did not intend, and intents.near accepts it because the signature still verifies over the altered payload?

## Target
- File/function: packages/intents-sdk/src/intents/intent-executer-impl/intent-executer.ts `signAndSendIntent`, `mergeIntentPayloads`, `composeMultiPayloads`; intent-payload-builder.ts; intent-payload-factory.ts; intent-signer-impl/*
- Entrypoint: `IntentsSDK.signAndSendIntent` / `intentBuilder()` / `sendSignedIntents`
- Attacker controls: `nonce` through via `sendSignedIntents(multiPayloads)` with a payload signed elsewhere; the `storage_deposit` intent body
- Exploit idea: the SDK only forwards; no check that fields match `envConfig`. For `sep53` the signed bytes are `computeSignedSep53Hash` (sha256 of 'Stellar Signed Message:\n' + payload).
- Invariant to test: signed.nonce == the value the caller constructed; for `intents`, the multiset of intents signed equals the multiset added (no reference-dedup collapse, no reorder).
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: use a `sep53` signer with a recording `signMessage`, apply the manipulation, decode the signed payload and diff every field.
