# Q3707: polynomials batch_invert one layer authorizes an

## Question
Can an unprivileged NEAR account enter through `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)` and use proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method to drive the code path through `crates/threshold-signatures/src/crypto/polynomials.rs::batch_invert` so that one layer authorizes an object another layer would not authorize, breaking the invariant that all codecs and DTO conversions must preserve the same canonical security meaning, and leading to Contract execution flows?

## Target
- File/function: crates/threshold-signatures/src/crypto/polynomials.rs:208::batch_invert
- Entrypoint: `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)`
- Attacker controls: proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method
- Exploit idea: one layer authorizes an object another layer would not authorize
- Invariant to test: all codecs and DTO conversions must preserve the same canonical security meaning
- Expected Immunefi impact: Contract execution flows
- Fast validation: round-trip the same attacker-chosen object through every codec used by the public flow and diff hashes, normalized fields, and authorization results
