# Q660: report data compute_public_keys_hash old enclave state remains

## Question
Can an unprivileged NEAR account or outsider node trying to look like a valid participant enter through `submit_participant_info / verify_tee` and use attestation bytes, node identity fields, responder/signer keys, repeated submissions, and timing around cleanup or re-verification to drive the code path through `crates/mpc-attestation/src/report_data.rs::compute_public_keys_hash` so that old enclave state remains good enough to authorize current signing behavior, breaking the invariant that attestation freshness must be rechecked against current identity, verifier set, and allowed measurements, and leading to Unauthorized access to MPC key shares or signing capability?

## Target
- File/function: crates/mpc-attestation/src/report_data.rs:92::compute_public_keys_hash
- Entrypoint: `submit_participant_info / verify_tee`
- Attacker controls: attestation bytes, node identity fields, responder/signer keys, repeated submissions, and timing around cleanup or re-verification
- Exploit idea: old enclave state remains good enough to authorize current signing behavior
- Invariant to test: attestation freshness must be rechecked against current identity, verifier set, and allowed measurements
- Expected Immunefi impact: Unauthorized access to MPC key shares or signing capability
- Fast validation: capture a once-valid attestation, mutate the associated participant identity or surrounding verifier configuration, and resubmit the old quote
