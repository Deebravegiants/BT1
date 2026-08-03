# Q1046: batch_all can bind approval to the wrong payload

## Question
Can an unprivileged attacker make `batch_all` approve or execute a different payload than users thought they had authorized because hashing, length, or metadata binding is incomplete?

## Target
- File/function: substrate/frame/utility/src/lib.rs::batch_all
- Entrypoint: public dispatch wrapper `batch_all`
- Attacker controls: nested call payloads, duplicate or adversarial list ordering, batched or wrapped execution context
- Exploit idea: Focus on call hash, encoded length, mortality, nonce, and fallback payload mismatches.
- Invariant to test: The payload users approve must be exactly the payload the runtime executes.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Mutate inert-looking fields, encoded lengths, and nested-call ordering while reusing the same outer approval or signature.
