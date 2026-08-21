# Q2140: Signed payload construction in RgbCameraMetadata is ambiguous (debug_report.rs)

## Question
Can an unprivileged attacker exploit non-canonical serialization in `RgbCameraMetadata` in [src/debug_report.rs](src/debug_report.rs) (map ordering, optional fields, unescaped separators) so two different logical payloads produce the same signed bytes, letting one Orb signature authenticate a different claim?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `RgbCameraMetadata` (type)
- Entrypoint: Attacker-controlled string fields that end up inside the signed payload
- Attacker controls: content of identity/metadata fields that are concatenated into the signed bytes
- Exploit idea: Look for length-prefixing and canonical encoding in `RgbCameraMetadata`; without it, field-boundary shifting creates collisions.
- Invariant to test: The signed byte string is an injective, canonical encoding of the logical payload.
- Expected Immunefi impact: Orb-signed attestation authenticating a claim the Orb never made
- Fast validation: Differential test constructing two distinct payloads through `RgbCameraMetadata` and asserting distinct signed bytes.
