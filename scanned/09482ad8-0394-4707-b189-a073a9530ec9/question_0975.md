# Q0975: Signature covers less than the security-relevant data in IrCameraMetadata (debug_report.rs)

## Question
Can an unprivileged attacker modify or influence a field that `IrCameraMetadata` in [src/debug_report.rs](src/debug_report.rs) transmits but excludes from the signed/committed bytes, so the backend trusts an unauthenticated field alongside a valid signature?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `IrCameraMetadata` (type)
- Entrypoint: Attacker-influenced metadata in the signup payload
- Attacker controls: the value of fields outside the signed region
- Exploit idea: Diff the transmitted structure against the signed structure in `IrCameraMetadata`.
- Invariant to test: Every field the backend acts upon is inside the signed/committed region.
- Expected Immunefi impact: Authenticated package carrying attacker-chosen unauthenticated fields
- Fast validation: Unit-test asserting the signed byte range in `IrCameraMetadata` covers the full transmitted structure.
