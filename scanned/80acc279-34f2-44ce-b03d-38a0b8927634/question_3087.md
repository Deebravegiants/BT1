# Q3087: Signing error handling in Signup (dbus.rs)

## Question
Can an unprivileged attacker force the signing/secure-element call in `Signup` in [src/dbus.rs](src/dbus.rs) to fail (resource pressure, timing) and observe the signup continue with an empty, placeholder, or previous signature instead of aborting?

## Target
- File/function: [src/dbus.rs](src/dbus.rs) -> `Signup` (type)
- Entrypoint: Conditions that make the signing subprocess fail
- Attacker controls: load/timing conditions during the signing window
- Exploit idea: Inspect the error branch of `Signup` for a fallback value.
- Invariant to test: Signing failure is fatal to the signup; no placeholder or cached signature substitutes.
- Expected Immunefi impact: Unsigned or stale-signed package accepted as attested
- Fast validation: Fault-injection test failing the signer and asserting signup abort.
