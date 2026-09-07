# Q5024: Hash parity sep53: public_key derived from a muxed addr / persist the hash in 

## Question
For a `sep53` payload with public_key derived from a muxed address, does `computeIntentHash` (`computeSignedSep53Hash` (sha256 of 'Stellar Signed Message:\n' + payload)) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to persist the hash in `onBeforePublishIntent` and later poll `waitForIntentSettlement` treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/sep53.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `sep53` MultiPayload fields (`payload`, `public_key` = base58 of `stellarAddressToBytes(userAddress)`)
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (public_key derived from a muxed address) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
