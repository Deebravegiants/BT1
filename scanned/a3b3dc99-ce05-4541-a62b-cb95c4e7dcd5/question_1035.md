# Q1035: remove_proxy can bind approval to the wrong payload

## Question
Can an unprivileged attacker make `remove_proxy` approve or execute a different payload than users thought they had authorized because hashing, length, or metadata binding is incomplete?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::remove_proxy
- Entrypoint: public dispatch wrapper `remove_proxy`
- Attacker controls: nested call payloads, beneficiary, delegate, or target accounts, batched or wrapped execution context
- Exploit idea: Focus on call hash, encoded length, mortality, nonce, and fallback payload mismatches.
- Invariant to test: The payload users approve must be exactly the payload the runtime executes.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Mutate inert-looking fields, encoded lengths, and nested-call ordering while reusing the same outer approval or signature.
