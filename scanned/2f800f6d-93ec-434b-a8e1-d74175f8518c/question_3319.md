# Q3319: Signed payload construction in IrCameraMetadata is ambiguous (debug_report.rs)

## Question
Can an unprivileged attacker exploit non-canonical serialization in `IrCameraMetadata` in [src/debug_report.rs](src/debug_report.rs) (map ordering, optional fields, unescaped separators) so two different logical payloads produce the same signed bytes, letting one Orb signature authenticate a different claim?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `IrCameraMetadata` (type)
- Entrypoint: Attacker-controlled string fields that end up inside the signed payload
- Attacker controls: content of identity/metadata fields that are concatenated into the signed bytes
- Exploit idea: Look for length-prefixing and canonical encoding in `IrCameraMetadata`; without it, field-boundary shifting creates collisions.
- Invariant to test: The signed byte string is an injective, canonical encoding of the logical payload.
- Expected Immunefi impact: Orb-signed attestation authenticating a claim the Orb never made
- Fast validation: Differential test constructing two distinct payloads through `IrCameraMetadata` and asserting distinct signed bytes.
