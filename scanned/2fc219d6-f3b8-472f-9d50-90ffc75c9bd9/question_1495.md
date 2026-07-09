# Q1495: generation triple_generation_max_incoming_buffer_entries session-local randomness or transcripts

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/threshold-signatures/src/ecdsa/ot_based_ecdsa/triples/generation.rs::triple_generation_max_incoming_buffer_entries` so that session-local randomness or transcripts get applied to the wrong request, breaking the invariant that all presign, transcript, and share state must be isolated per logical signing session, and leading to Unauthorized transaction?

## Target
- File/function: crates/threshold-signatures/src/ecdsa/ot_based_ecdsa/triples/generation.rs:774::triple_generation_max_incoming_buffer_entries
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: session-local randomness or transcripts get applied to the wrong request
- Invariant to test: all presign, transcript, and share state must be isolated per logical signing session
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: run concurrent sign requests that differ only in one critical field and trace whether any intermediate identifiers or share material cross between sessions
