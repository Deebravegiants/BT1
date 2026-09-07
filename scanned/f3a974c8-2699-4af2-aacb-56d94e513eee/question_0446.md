# Q0446: Hash parity ton_connect: `timestamp` > 2^31 (after 2038) or a / persist the hash in 

## Question
For a `ton_connect` payload with `timestamp` > 2^31 (after 2038) or a float, does `computeIntentHash` (`computeTonConnectHash` (0xffff || 'ton-connect/sign-data/' || wc || addr || domain_len || domain || ts || 'txt' || len || text)) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to persist the hash in `onBeforePublishIntent` and later poll `waitForIntentSettlement` treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/ton-connect.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `ton_connect` MultiPayload fields (`address`, `domain`, `timestamp`, `payload.text`, `public_key` derived from `userAddress`)
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (`timestamp` > 2^31 (after 2038) or a float) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
