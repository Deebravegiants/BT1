# Q0781: Signing error handling in from (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker force the signing/secure-element call in `from` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) to fail (resource pressure, timing) and observe the signup continue with an empty, placeholder, or previous signature instead of aborting?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `from` (function)
- Entrypoint: Conditions that make the signing subprocess fail
- Attacker controls: load/timing conditions during the signing window
- Exploit idea: Inspect the error branch of `from` for a fallback value.
- Invariant to test: Signing failure is fatal to the signup; no placeholder or cached signature substitutes.
- Expected Immunefi impact: Unsigned or stale-signed package accepted as attested
- Fast validation: Fault-injection test failing the signer and asserting signup abort.
