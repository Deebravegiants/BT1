# Q1439: ecdsa triple_store_for_t session-local randomness or transcripts

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/providers/ecdsa.rs::triple_store_for_t` so that session-local randomness or transcripts get applied to the wrong request, breaking the invariant that all presign, transcript, and share state must be isolated per logical signing session, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/providers/ecdsa.rs:125::triple_store_for_t
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: session-local randomness or transcripts get applied to the wrong request
- Invariant to test: all presign, transcript, and share state must be isolated per logical signing session
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: run concurrent sign requests that differ only in one critical field and trace whether any intermediate identifiers or share material cross between sessions
