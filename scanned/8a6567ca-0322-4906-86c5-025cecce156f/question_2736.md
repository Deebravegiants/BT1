# Q2736: Hash parity erc191: payload with CRLF line endings from  / persist the hash in 

## Question
For a `erc191` payload with payload with CRLF line endings from a wallet, does `computeIntentHash` (`computeSignedErc191Hash` (keccak256 of `\x19Ethereum Signed Message:\n<len>` + payload)) return a different value than the `intent_hash` intents.near/relayer derive, so an integrator that uses the local hash to persist the hash in `onBeforePublishIntent` and later poll `waitForIntentSettlement` treats a settled withdrawal as missing and re-sends it, paying the user twice?

## Target
- File/function: packages/intents-sdk/src/intents/intent-hash.ts `computeIntentHash`; intent-hashes/erc191.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` with `onBeforePublishIntent`; `sendSignedIntents`
- Attacker controls: the `erc191` MultiPayload fields (`payload` = JSON of {signer_id, verifying_contract, deadline, nonce, intents})
- Exploit idea: Local hashing is a re-implementation of near/intents `multi.rs`; any encoding divergence (payload with CRLF line endings from a wallet) yields a hash that never appears in `get_status`.
- Invariant to test: computeIntentHash(mp) == relayer intent_hash for the same mp, for all valid inputs.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: fixture payloads with the edge input; compare with hashes produced by the reference Rust implementation / relayer responses.
