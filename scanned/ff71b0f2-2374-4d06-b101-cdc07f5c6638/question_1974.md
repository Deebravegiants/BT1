# Q1974: Hash parity nep413: a `nonce` that is not exactly 32 byt / persist the hash in 

## Question
For a `nep413` payload with a `nonce` that is not exactly 32 bytes after base64 decode, does `computeIntentHash` (`computeSignedNep413Hash` -> `hashNEP413Message`) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to persist the hash in `onBeforePublishIntent` and later poll `waitForIntentSettlement` treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/nep413.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `nep413` MultiPayload fields (`message` = JSON of {deadline, intents, signer_id}; `recipient` = verifying_contract; `nonce` base64 (32 bytes))
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (a `nonce` that is not exactly 32 bytes after base64 decode) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
