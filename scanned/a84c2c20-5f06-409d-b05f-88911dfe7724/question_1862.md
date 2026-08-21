# Q1862: Signing error handling in make_iris_tar (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker force the signing/secure-element call in `make_iris_tar` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) to fail (resource pressure, timing) and observe the signup continue with an empty, placeholder, or previous signature instead of aborting?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_iris_tar` (function)
- Entrypoint: Conditions that make the signing subprocess fail
- Attacker controls: load/timing conditions during the signing window
- Exploit idea: Inspect the error branch of `make_iris_tar` for a fallback value.
- Invariant to test: Signing failure is fatal to the signup; no placeholder or cached signature substitutes.
- Expected Immunefi impact: Unsigned or stale-signed package accepted as attested
- Fast validation: Fault-injection test failing the signer and asserting signup abort.
