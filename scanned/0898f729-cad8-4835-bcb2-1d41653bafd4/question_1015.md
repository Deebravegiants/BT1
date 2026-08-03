# Q1015: set_primary_username can bind approval to the wrong payload

## Question
Can an unprivileged attacker make `set_primary_username` approve or execute a different payload than users thought they had authorized because hashing, length, or metadata binding is incomplete?

## Target
- File/function: substrate/frame/identity/src/lib.rs::set_primary_username
- Entrypoint: signed extrinsic `set_primary_username`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Focus on call hash, encoded length, mortality, nonce, and fallback payload mismatches.
- Invariant to test: The payload users approve must be exactly the payload the runtime executes.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Mutate inert-looking fields, encoded lengths, and nested-call ordering while reusing the same outer approval or signature.
