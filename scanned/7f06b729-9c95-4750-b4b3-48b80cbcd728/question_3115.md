# Q3115: Hash parity tip191: payload re-serialised by the wallet  / persist the hash in 

## Question
For a `tip191` payload with payload re-serialised by the wallet with different key order, does `computeIntentHash` (`computeSignedTip191Hash` (keccak256 of `\x19TRON Signed Message:\n<len>` + payload)) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to persist the hash in `onBeforePublishIntent` and later poll `waitForIntentSettlement` treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/tip191.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `tip191` MultiPayload fields (`payload` string as signed by TronLink)
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (payload re-serialised by the wallet with different key order) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
