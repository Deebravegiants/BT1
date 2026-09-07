# Q5788: Hash parity raw_ed25519: public_key = `ed25519:` + a non-base / persist the hash in 

## Question
For a `raw_ed25519` payload with public_key = `ed25519:` + a non-base58 userAddress, does `computeIntentHash` (`computeSignedRawEd25519Hash` (sha256 of payload)) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to persist the hash in `onBeforePublishIntent` and later poll `waitForIntentSettlement` treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/raw-ed25519.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `raw_ed25519` MultiPayload fields (`payload` = UTF-8 of the message bytes; `public_key` = `ed25519:<userAddress>`)
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (public_key = `ed25519:` + a non-base58 userAddress) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
