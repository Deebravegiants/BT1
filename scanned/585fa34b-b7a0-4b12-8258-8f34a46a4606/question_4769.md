# Q4769: Hash parity sep53: payload signed by Freighter with tra / dedupe retries by in

## Question
For a `sep53` payload with payload signed by Freighter with trailing newline, does `computeIntentHash` (`computeSignedSep53Hash` (sha256 of 'Stellar Signed Message:\n' + payload)) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to dedupe retries by intent hash before re-publishing treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/sep53.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `sep53` MultiPayload fields (`payload`, `public_key` = base58 of `stellarAddressToBytes(userAddress)`)
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (payload signed by Freighter with trailing newline) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
