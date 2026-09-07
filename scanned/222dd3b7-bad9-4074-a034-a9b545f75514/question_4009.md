# Q4009: Hash parity webauthn: `client_data_json` challenge not equ / dedupe retries by in

## Question
For a `webauthn` payload with `client_data_json` challenge not equal to sha256(payload), does `computeIntentHash` (`computeSignedWebAuthnHash` (sha256 of payload only)) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to dedupe retries by intent hash before re-publishing treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/webauthn.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `webauthn` MultiPayload fields (`payload`, `client_data_json`, `authenticator_data`, `public_key` p256:/ed25519:)
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (`client_data_json` challenge not equal to sha256(payload)) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
